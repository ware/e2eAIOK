#python -m unittest tests/test_spark_dataprocessor.py
#python -m unittest tests.test_feature_wrangler.TestFeatureWranglerPandasBased
#python -m unittest tests.test_feature_wrangler.TestFeatureWranglerSparkBased

#python -m unittest tests.test_relational_builder.TestRelationalBuilder
#python -m unittest tests.test_pipeline_json.TestPipielineJson
python -m unittest tests.test_pipeline_json.TestPipielineJson.test_import_nyc
python -m unittest tests.test_pipeline_json.TestPipielineJson.test_import_twitter
python -m unittest tests.test_pipeline_json.TestPipielineJson.test_import_amazon
python -m unittest tests.test_pipeline_json.TestPipielineJson.test_import_nyc_execute_spark
python -m unittest tests.test_pipeline_json.TestPipielineJson.test_import_twitter_execute_spark
python -m unittest tests.test_pipeline_json.TestPipielineJson.test_import_amazon_execute_spark
