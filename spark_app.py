#!/usr/bin/env python
"""
Smart Energy Consumption Analytics - Apache Spark Application
Batch processing for energy consumption data analysis
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, to_timestamp, year, month, dayofweek, hour
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
import os
from datetime import datetime

def create_spark_session(app_name="Smart Energy Analytics"):
    """
    Create and configure Spark Session
    
    Args:
        app_name: Name of the Spark application
    
    Returns:
        SparkSession object
    """
    spark = (SparkSession
             .builder
             .appName(app_name)
             .config("spark.driver.memory", "2g")
             .config("spark.executor.memory", "2g")
             .config("spark.sql.shuffle.partitions", "200")
             .config("spark.local.dir", "/tmp")
             .getOrCreate())
    
    # Set log level
    spark.sparkContext.setLogLevel("INFO")
    
    print(f"✓ Spark Session created: {app_name}")
    print(f"  - Version: {spark.version}")
    print(f"  - Driver Memory: 2g")
    print(f"  - Executor Memory: 2g")
    print(f"  - Shuffle Partitions: 200")
    
    return spark

def load_data(spark, data_path):
    """
    Load CSV data into Spark DataFrame
    
    Args:
        spark: SparkSession object
        data_path: Path to input CSV file
    
    Returns:
        Spark DataFrame
    """
    print(f"\n📂 Loading data from: {data_path}")
    
    try:
        df = (spark.read
              .option("header", "true")
              .option("inferSchema", "true")
              .csv(data_path))
        
        print(f"✓ Data loaded successfully")
        print(f"  - Rows: {df.count():,}")
        print(f"  - Columns: {len(df.columns)}")
        
        return df
    
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        raise

def data_quality_checks(df):
    """
    Perform data quality validation
    
    Args:
        df: Spark DataFrame
    """
    print("\n🔍 Data Quality Checks")
    print(f"  - Total Rows: {df.count():,}")
    print(f"  - Total Columns: {len(df.columns)}")
    print(f"  - Schema: {df.printSchema()}")
    
    # Check for null values
    print("\n  Null Value Analysis:")
    null_counts = []
    for col_name in df.columns:
        null_count = df.filter(col(col_name).isNull()).count()
        if null_count > 0:
            print(f"    - {col_name}: {null_count:,} nulls")
            null_counts.append((col_name, null_count))
    
    if not null_counts:
        print("    ✓ No null values found")
    
    # Data types
    print("\n  Data Types:")
    for field in df.schema.fields:
        print(f"    - {field.name}: {field.dataType}")

def data_cleaning(df):
    """
    Clean and transform data
    
    Args:
        df: Spark DataFrame
    
    Returns:
        Cleaned Spark DataFrame
    """
    print("\n🧹 Data Cleaning")
    
    # Remove duplicates
    initial_count = df.count()
    df_clean = df.dropDuplicates()
    removed_count = initial_count - df_clean.count()
    print(f"  ✓ Duplicate rows removed: {removed_count:,}")
    
    # Convert Datetime to timestamp if it exists
    if "Datetime" in df_clean.columns:
        df_clean = (df_clean
                   .withColumn("Datetime", 
                              to_timestamp(col("Datetime"), "M/d/yyyy H:mm")))
        print(f"  ✓ Datetime column converted to timestamp format")
    
    print(f"  ✓ Clean data rows: {df_clean.count():,}")
    
    return df_clean

def analyze_data(df):
    """
    Perform statistical analysis
    
    Args:
        df: Spark DataFrame
    """
    print("\n📊 Data Analysis")
    
    # Show schema
    print("  Schema:")
    df.printSchema()
    
    # Statistical summary
    print("\n  Statistical Summary:")
    numeric_columns = [field.name for field in df.schema.fields 
                      if field.dataType in [DoubleType(), 'double']]
    
    if numeric_columns:
        df.describe(*numeric_columns).show()
    else:
        print("    No numeric columns found for summary statistics")
    
    # Show sample data
    print("\n  Sample Data (first 5 rows):")
    df.show(5)

def save_results(df, output_path):
    """
    Save results to CSV format
    
    Args:
        df: Spark DataFrame
        output_path: Path to output directory
    """
    print(f"\n💾 Saving Results to: {output_path}")
    
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Write results as CSV
        (df.coalesce(1)
         .write
         .format("csv")
         .mode("overwrite")
         .option("header", "true")
         .save(output_path))
        
        # List output files
        output_files = [f for f in os.listdir(output_path) if f.endswith('.csv')]
        print(f"✓ Results saved successfully")
        print(f"  - Output files: {len(output_files)}")
        for file in output_files:
            file_path = os.path.join(output_path, file)
            file_size = os.path.getsize(file_path)
            print(f"    - {file}: {file_size:,} bytes")
    
    except Exception as e:
        print(f"✗ Error saving results: {e}")
        raise

def main():
    """
    Main application flow
    """
    print("=" * 60)
    print("Smart Energy Consumption Analytics - Spark Application")
    print("=" * 60)
    
    # Configuration
    input_data = os.getenv("INPUT_DATA", "/data/powerconsumption.csv")
    output_dir = os.getenv("OUTPUT_DIR", "/output/results")
    
    print(f"\n⚙️  Configuration:")
    print(f"  - Input Data: {input_data}")
    print(f"  - Output Directory: {output_dir}")
    print(f"  - Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Create Spark Session
    spark = create_spark_session()
    
    try:
        # Load data
        df = load_data(spark, input_data)
        
        # Quality checks
        data_quality_checks(df)
        
        # Clean data
        df_clean = data_cleaning(df)
        
        # Analyze data
        analyze_data(df_clean)
        
        # Save results
        save_results(df_clean, output_dir)
        
        print("\n" + "=" * 60)
        print("✅ Application completed successfully!")
        print("=" * 60)
    
    except Exception as e:
        print(f"\n❌ Application failed with error: {e}")
        print("=" * 60)
        raise
    
    finally:
        # Stop Spark Session
        spark.stop()
        print("✓ Spark Session stopped")

if __name__ == "__main__":
    main()
