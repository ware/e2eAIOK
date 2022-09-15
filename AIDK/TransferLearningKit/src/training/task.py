#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author : Hua XiaoZhuan          
# @Time   : 8/19/2022 10:08 AM
import torch
import torchvision.models
from torch.utils.data import Dataset
from torch.utils.data import random_split
from torch.utils.tensorboard import SummaryWriter
from torch.utils.data.distributed import DistributedSampler
from engine_core.backbone.factory import createBackbone
from engine_core.finetunner.basic_finetunner import BasicFinetunner
from engine_core.transferrable_model import make_transferrable_with_finetune,set_attribute
from .train import Trainer,Evaluator
import torch.optim as optim
from .utils import EarlyStopping,initWeights,Timer
import logging
from functools import partial
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.distributed.optim.zero_redundancy_optimizer import ZeroRedundancyOptimizer as ZeRO
from torch.distributed.algorithms.join import Join
from torch.profiler import profile, ProfilerActivity

def trace_handler(trace_file,p):
    ''' profile trace handler

    :param trace_file: output trace file
    :param p: profiler
    :return:
    '''
    logging.info("trace_output:%s"%p.key_averages().table(sort_by="cpu_time_total", row_limit=20))
    p.export_chrome_trace(trace_file + str(p.step_num) + ".json")

class Task:
    ''' A whole training Task

    '''
    def __init__(self,**kwargs):
        self._kwargs = kwargs
        # parameters:
        ############### global ##############
        # is_distributed : whether is distributed
        # enable_transfer_learning : whether use transfer learning
        # training_epochs : training epochs
        # logging_interval_step : logging interval step
        # validate_metric_fn_map : validate metric function map
        # earlystop_metric : early stop metric
        # rank : rank
        # model_saved_path: model saved path
        ############### dataloader #############
        # data_train_dataset : train dataset
        # data_validate_dataset : validate dataset
        # data_test_dataset : test dataset
        # data_num_workers : data num workers
        # data_batch_size : data batch size
        # data_drop_last : whether drop last
        ############## model ############
        # model_num_classes : num classes
        # model_backbone_name : backbone name
        # model_loss : loss function
        # finetune_pretrained_path : pretrained model path
        # finetune_top_finetuned_layer : layer under which is used for finetuning
        # finetune_frozen : frozen finetune layer
        # finetune_pretrained_num_classes : num classes of pretrained model

        ############## optimizer ############
        # optimizer_learning_rate : learning rate
        # optimizer_weight_decay : weight decay
        # optimizer_momentum : momentum
        ############### lr_scheduler ##########
        # scheduler_T_max : scheduler T_max

        ######## tensorboard_writer ########
        # tensorboard_dir: tensorboard dir
        # tensorboard_filename_suffix : tensorboard filename suffix

        ######### early_stopping ###########
        # earlystop_tolerance_epoch : tolerance epoch
        # earlystop_delta : delta
        # earlystop_is_max : is max or min

        ######### profiler ##############
        # profile_skip_first: skip first n iteration
        # profile_wait : wait the next n iteration
        # profile_warmup : do profile, but not use in the next n iteration
        # profile_active : active in the next n iteration
        # profile_repeat : repeat k cycle
        # profile_activities : record CPU or CUDA, can be 'cpu','cuda', or 'cpu,cuda'
        # profile_trace_file_training : output to this file when training
        # profile_trace_file_inference : output to this file when inference
    def _create_dataloader(self):
        ''' create dataloader

        :return: (train_loader,validate_loader,test_loader)
        '''

        is_distributed = self._kwargs['is_distributed']
        train_dataset = self._kwargs['data_train_dataset']
        validate_dataset = self._kwargs['data_validate_dataset']
        test_dataset = self._kwargs['data_test_dataset']
        num_workers = self._kwargs['data_num_workers']
        batch_size = self._kwargs['data_batch_size']
        data_drop_last = self._kwargs['data_drop_last']

        logging.info("train_dataset:" + str(train_dataset))
        logging.info("validate_dataset:" + str(validate_dataset))
        logging.info("test_dataset:" + str(test_dataset))

        if is_distributed:
            train_loader = torch.utils.data.DataLoader(train_dataset,  # only split train dataset
                                                       batch_size=batch_size, shuffle=False,
                                                       # shuffle is conflict with sampler
                                                       num_workers=num_workers, drop_last=data_drop_last,
                                                       sampler=DistributedSampler(train_dataset))
        else:
            train_loader = torch.utils.data.DataLoader(train_dataset,  # only split train dataset
                                                       batch_size=batch_size, shuffle=True,
                                                       # shuffle is conflict with sampler
                                                       num_workers=num_workers, drop_last=data_drop_last)
        validate_loader = torch.utils.data.DataLoader(validate_dataset,
                                                      batch_size=batch_size, shuffle=True,
                                                      num_workers=num_workers, drop_last=data_drop_last)
        if test_dataset is not None:
            test_loader = torch.utils.data.DataLoader(test_dataset,
                                                  batch_size=batch_size, shuffle=True,
                                                  num_workers=num_workers, drop_last=data_drop_last)
        else:
            test_loader = None
        self._train_loader = train_loader     # may be use by other component
        self._epoch_steps = len(train_loader) # may be use by other component
        logging.info("epoch_steps:%s" % self._epoch_steps)
        return (train_loader, validate_loader, test_loader)
    def _create_model(self):
        ''' create model

        :return: a model
        '''
        is_distributed = self._kwargs['is_distributed']
        enable_transfer_learning = self._kwargs['enable_transfer_learning']
        num_classes = self._kwargs['model_num_classes']
        backbone_name = self._kwargs['model_backbone_name']
        loss = self._kwargs['model_loss']
        pretrained_path = self._kwargs['finetune_pretrained_path']
        top_finetuned_layer = self._kwargs['finetune_top_finetuned_layer']
        finetune_frozen = self._kwargs['finetune_frozen']
        pretrained_num_classes = self._kwargs['finetune_pretrained_num_classes']

        model = createBackbone(backbone_name, num_classes=num_classes)
        model.apply(initWeights) # init weight
        set_attribute("model", model, "loss", loss)

        logging.info('backbone:%s' % model)

        if enable_transfer_learning:
            pretrained_model = createBackbone(backbone_name, num_classes=pretrained_num_classes)
            pretrained_model.load_state_dict(torch.load(pretrained_path)['net'], strict=True)
            finetunner = BasicFinetunner(pretrained_model, top_finetuned_layer=top_finetuned_layer, is_frozen=finetune_frozen)
            model = make_transferrable_with_finetune(model, loss, finetunner=finetunner)
            model.init_weight()
            logging.info('finetunner:%s' % finetunner)
            logging.info('transferrable model:%s' % model)


        if is_distributed:
            logging.info("training with DistributedDataParallel")
            model = DDP(model)
        logging.info("model:%s"%model)
        self._model = model # may be use by other component
        return model
    def _create_optimizer(self):
        ''' create optimizer

        :return: an optimizer
        '''
        is_distributed = self._kwargs['is_distributed']
        learning_rate = self._kwargs['optimizer_learning_rate']
        weight_decay = self._kwargs['optimizer_weight_decay']
        momentum = self._kwargs['optimizer_momentum']

        if is_distributed:
            logging.info("training with DistributedDataParallel")
            optimizer = ZeRO(filter(lambda p: p.requires_grad, self._model.parameters()), optim.SGD,
                             lr=learning_rate, weight_decay=weight_decay,momentum=momentum)
        else:
            optimizer = optim.SGD(filter(lambda p: p.requires_grad, self._model.parameters()),
                                  lr=learning_rate, weight_decay=weight_decay,momentum=momentum)
        logging.info("optimizer:%s"%optimizer)
        self._optimizer = optimizer # may be use by other component
        return optimizer
    def _create_lr_scheduler(self):
        ''' create lr_scheduler

        :return: a lr_scheduler
        '''
        T_max = self._kwargs['scheduler_T_max']
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(self._optimizer, T_max=T_max)
        return scheduler
    def _create_tensorboard_writer(self):
        ''' create tensorboard_writer

        :return: a tensorboard_writer
        '''
        tensorboard_dir = self._kwargs['tensorboard_dir']
        tensorboard_filename_suffix = self._kwargs['tensorboard_filename_suffix']
        tensorboard_writer = SummaryWriter(tensorboard_dir, filename_suffix=tensorboard_filename_suffix)
        logging.info('tensorboard_writer :%s' % tensorboard_writer)
        return tensorboard_writer
    def _create_early_stopping(self):
        ''' create early_stopping

        :return: an early_stopping
        '''
        tolerance_epoch = self._kwargs['earlystop_tolerance_epoch']
        if tolerance_epoch <= 0:
            return None

        delta = self._kwargs['earlystop_delta']
        is_max = self._kwargs['earlystop_is_max']
        early_stopping = EarlyStopping(tolerance_epoch=tolerance_epoch, delta=delta, is_max=is_max)
        logging.info('early_stopping :%s' % early_stopping)
        return early_stopping
    def _create_profiler(self):
        ''' create a profiler

        :return: (training_profiler,inference_profiler)
        '''
        skip_first = self._kwargs['profile_skip_first']
        wait = self._kwargs['profile_wait']
        warmup = self._kwargs['profile_warmup']
        active = self._kwargs['profile_active']
        repeat = self._kwargs['profile_repeat']
        def parse_activities(activity_str):
            result = set()
            for item in activity_str.lower().split(","):
                if item == 'cpu':
                    result.add(ProfilerActivity.CPU)
                elif item == 'gpu' or item == 'cuda':
                    result.add(ProfilerActivity.CUDA)
            return result
        activities = parse_activities(self._kwargs['profile_activities'])
        training_trace_file = self._kwargs['profile_trace_file_training']
        inference_trace_file = self._kwargs['profile_trace_file_inference']

        schedule = torch.profiler.schedule(skip_first=skip_first,wait=wait,
            warmup=warmup,active=active,repeat=repeat)
        training_profiler = profile(activities=activities,schedule=schedule,
                           on_trace_ready=partial(trace_handler,training_trace_file))
        inference_profiler = profile(activities=activities, schedule=schedule,
                                   on_trace_ready=partial(trace_handler, inference_trace_file))
        logging.info("training_profiler:%s"%training_profiler)
        logging.info("inference_profiler:%s" % inference_profiler)
        return (training_profiler,inference_profiler)
    def _load_trained_model(self):
        ''' load the trained model

        :return: a trained model
        '''
        num_classes = self._kwargs['model_num_classes']
        loss = self._kwargs['model_loss']
        model_saved_path = self._kwargs['model_saved_path']
        backbone_name = self._kwargs['model_backbone_name']

        trained_model = createBackbone(backbone_name, num_classes=num_classes)
        trained_model.load_state_dict(torch.load(model_saved_path))
        set_attribute("trained_model", trained_model, "loss",loss)
        return trained_model
    def run(self):
        training_epochs = self._kwargs['training_epochs']
        logging_interval_step = self._kwargs['logging_interval_step']
        validate_metric_fn_map = self._kwargs['validate_metric_fn_map']
        earlystop_metric = self._kwargs['earlystop_metric']
        rank = self._kwargs['rank']
        is_distributed = self._kwargs['is_distributed']
        model_saved_path = self._kwargs['model_saved_path']
        ######################### create components #########################
        (train_loader, validate_loader, test_loader) = self._create_dataloader()
        model = self._create_model()
        optimizer = self._create_optimizer()
        lr_scheduler = self._create_lr_scheduler()
        tensorboard_writer = self._create_tensorboard_writer()
        early_stopping = self._create_early_stopping()
        training_profiler, inference_profiler = self._create_profiler()
        trainer = Trainer(model, optimizer, lr_scheduler, early_stopping, validate_metric_fn_map,
                          earlystop_metric, training_epochs,
                          tensorboard_writer,training_profiler, logging_interval_step,rank=rank)
        logging.info("trainer:%s" % trainer)
        evaluator = Evaluator(validate_metric_fn_map, tensorboard_writer,inference_profiler)
        logging.info("evaluator:%s" % evaluator)
        #################################### train and evaluate ###################
        with Timer():
            if is_distributed:
                with Join([model, optimizer]):
                    trainer.train(train_loader, self._epoch_steps, validate_loader, model_saved_path)
            else:
                trainer.train(train_loader, self._epoch_steps, validate_loader, model_saved_path)
        ################################### test ###################################
        if test_loader is not None:
            if (not is_distributed) or (is_distributed and rank == 0):  # only test once
                trained_model = self._load_trained_model()
                with Timer():
                    evaluator.evaluate(trained_model, test_loader)
