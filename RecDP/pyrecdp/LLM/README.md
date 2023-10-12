# RecDP LLM - LLM data preparation utility

RecDP LLM is a set of python components that enables quick and easy establish of your own LLM data preparation pipeline.
* 10 general LLM data process components for Foundation model and finetune model training.
* 4 LLM data quality enhancement module for finetune model training
* 2 use cases for foundation model data prepration and finetune model data preparation.

## General - Foundation & FineTune

| Type                                                                                                                       | notebook                                                                                                                                                                                                   | Description                                               | supports                                             | Verified dataset & size               |
| -------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- | ---------------------------------------------------- | ------------------------------------- |
| [ Filter ](https://github.com/intel/e2eAIOK/blob/main/RecDP/pyrecdp/primitives/operations/text_filter.py)                         | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/intel/e2eAIOK/blob/main/RecDP/examples/notebooks/llmutils/filter.ipynb)              | Filter out document based on condition                    | profanity-based, black-list, url_based, length_based | RedPajama - 2 TB                      |
| [ Text Bytesize ](https://github.com/intel/e2eAIOK/blob/main/RecDP/pyrecdp/primitives/operations/text_bytesize.py)                         | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/intel/e2eAIOK/blob/main/RecDP/examples/notebooks/llmutils/bytesize.ipynb)              | Get text bytes size                    |  | RedPajama - 2 TB                      |
| [ Text Fixer ](https://github.com/intel/e2eAIOK/blob/main/RecDP/pyrecdp/primitives/operations/text_fixer.py)                 | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/intel/e2eAIOK/blob/main/RecDP/examples/notebooks/llmutils/text_fixer.ipynb)          | Clean repeated format in html, latex, codes               | html, latex, codes                                   | RefinedWeb - 1.7 TB                   |
| [ Language Identify ](https://github.com/intel/e2eAIOK/blob/main/RecDP/pyrecdp/primitives/operations/text_language_identify.py)   | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/intel/e2eAIOK/blob/main/RecDP/examples/notebooks/llmutils/language_identify.ipynb)   | Inentify major language type of document                  | en, zh, fr, de, .. total 25 langs                    | RedPajama - 2 TB                      |
| [ Fuzzy Deduplicator ](https://github.com/intel/e2eAIOK/blob/main/RecDP/pyrecdp/primitives/operations/text_deduplication.py#L99)           | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/intel/e2eAIOK/blob/main/RecDP/examples/notebooks/llmutils/fuzzy_deduplication.ipynb) | Detect and reduce duplication based on document context   | minHashLSH                     | PILE - 200 GB                         |
| [ Global Decuplicator ](https://github.com/intel/e2eAIOK/blob/main/RecDP/pyrecdp/primitives/operations/text_deduplication.py#L194)         | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/intel/e2eAIOK/blob/main/RecDP/examples/notebooks/llmutils/decontamination.ipynb)     | Detect and reduce duplication based on exact same content | sha256-hash                                          | RefinedWeb - 1.7 TB, RedPajama - 2 TB |
| [ Document splitter  ](https://github.com/intel/e2eAIOK/blob/main/RecDP/pyrecdp/primitives/operations/text_split.py)     | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/intel/e2eAIOK/blob/main/RecDP/examples/notebooks/llmutils/document_split.ipynb)      | Split Document into multiple sub documents                | chapter_based, length_based                          | RefinedWeb - 1.7 TB                   |
| [ PII Removal ](https://github.com/intel/e2eAIOK/blob/main/RecDP/pyrecdp/primitives/operations/text_pii_remove.py)                | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/intel/e2eAIOK/blob/main/RecDP/examples/notebooks/llmutils/pii_removal.ipynb)         | Detect and replace personal infomation in document        | email, phone, ip, username, password                 | RefinedWeb - 1.7 TB                   |
| [ Reader ](https://github.com/intel/e2eAIOK/blob/main/RecDP/pyrecdp/primitives/operations/text_reader.py#L16)                      | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/intel/e2eAIOK/blob/main/RecDP/examples/notebooks/llmutils/reader.ipynb)            | Read data from directory                            | jsonl, parquet,                                 | RefinedWeb - 1.7 TB                   |
| [ Converter ](https://github.com/intel/e2eAIOK/blob/main/RecDP/pyrecdp/primitives/operations/text_converter.py)                      | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/intel/e2eAIOK/blob/main/RecDP/examples/notebooks/llmutils/convert.ipynb)            | Read and convert unstructed data to unified format                           | html, document, image, pdf, ...                                 | RefinedWeb - 1.7 TB                   |
| [ Writer ](https://github.com/intel/e2eAIOK/blob/main/RecDP/pyrecdp/primitives/operations/text_writer.py#L7)                      | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/intel/e2eAIOK/blob/main/RecDP/examples/notebooks/llmutils/writer.ipynb)            | write data to directory                            | jsonl, parquet                               | RefinedWeb - 1.7 TB                   |
| [ ClassifyWriter ](https://github.com/intel/e2eAIOK/blob/main/RecDP/pyrecdp/primitives/operations/text_writer.py#L47)                      | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/intel/e2eAIOK/blob/main/RecDP/examples/notebooks/llmutils/classify.ipynb)            | Classify and write data into sub buckets                            | meta fields, language                                | RefinedWeb - 1.7 TB                   |
| [ Prompt Enhancement ](#)                                                                                                       | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/intel/e2eAIOK/blob/main/RecDP/examples/notebooks/llmutils/prompt_enhancement.ipynb)      | creates high-complexity instructions from existing instruct-tuned LLM models       | PromptSource, self-instruct, evol-instruct(wizardLM) | alpaca |

## LLM Data Quality Analysis

| Diversity   |  GPT-3 Scoring | Toxicity | 
| :-------- | :---------- | :------------|
| Visualize the diversity distribution of data | Leverage GPT-3 to scoring | Visualize Toxicity probability |
| ![diversity](/RecDP/resources/diversity_analysis.png) | ![quality](/RecDP/resources/quality_scoring.png) | ![toxicity](/RecDP/resources/toxicity_analysis.png)|
| [learn more](https://colab.research.google.com/github/intel/e2eAIOK/blob/main/RecDP/examples/notebooks/llmutils/text_quality_assessment.ipynb) | [learn more](https://colab.research.google.com/github/intel/e2eAIOK/blob/main/RecDP/examples/notebooks/llmutils/data_diversity_control.ipynb) | [learn more](https://colab.research.google.com/github/intel/e2eAIOK/blob/main/RecDP/examples/notebooks/llmutils/toxicity_bias_control.ipynb) |


# Getting Start

## Deploy
```
DEBIAN_FRONTEND=noninteractive apt-get install -y openjdk-8-jre
pip install pyrecdp --pre
```

## * run with pipeline
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/intel/e2eAIOK/blob/main/RecDP/examples/notebooks/llmutils/resumable_pipeline.ipynb) 
```
from pyrecdp.primitives.operations import *
from pyrecdp.LLM import TextPipeline
from IPython.display import display

from pyrecdp.primitives.operations import *
from pyrecdp.LLM import ResumableTextPipeline

pipeline = ResumableTextPipeline()
ops = [
    JsonlReader("data/"),
    URLFilter(),
    LengthFilter(),
    ProfanityFilter(),
    TextFix(),
    LanguageIdentify(),
    PIIRemoval(),
    PerfileParquetWriter("ResumableTextPipeline_output")
]
pipeline.add_operations(ops)
pipeline.execute()
pipeline.export_to_yaml("custom_llm_data_pipeline.yaml")
```
or
```
from pyrecdp.LLM import ResumableTextPipeline
pipeline = TextPipeline("custom_llm_data_pipeline.yaml")
ret = pipeline.execute()
```

## * run with individual component
  * cmdline mode 
```
python pyrecdp/primitives/llmutils/language_identify.py \
    --data_dir tests/llm_data \
    --language_identify_output_dir output \
    --fasttext_model_dir ./cache/RecDP/models/lib.bin

```
  * operation-based API - ray mode
```
from pyrecdp.primitives.operations import LengthFilter
 
dataset = … # Ray Dataset
op = LengthFilter()
op.process_rayds(dataset)
```

  * operation-based API - spark mode
```
from pyrecdp.primitives.operations import LengthFilter

sparkdf = … # Spark Dataframe
op = LengthFilter()
op.process_spark(sparkdf)
```