import pandas as pd
import json
import os
from typing import Optional

try:
    import pyarrow.parquet as pq
    PYARROW_AVAILABLE = True
except ImportError:
    PYARROW_AVAILABLE = False

try:
    from avro.datafile import DataFileReader
    from avro.io import DatumReader
    AVRO_AVAILABLE = True
except ImportError:
    AVRO_AVAILABLE = False

class DatabaseConverter:
    """Handles database and big-data format conversions"""
    
    @staticmethod
    async def convert(input_path: str, output_path: str, 
                     source_format: str, target_format: str) -> str:
        """Main conversion dispatcher"""
        
        source_format = source_format.lower().replace('.', '')
        target_format = target_format.lower().replace('.', '')
        
        conversion_key = f"{source_format}_to_{target_format}"
        
        converters = {
            'sql_to_csv': DatabaseConverter.sql_to_csv,
            'csv_to_sql': DatabaseConverter.csv_to_sql,
            'json_to_sql': DatabaseConverter.json_to_sql,
            'xlsx_to_sql': DatabaseConverter.excel_to_sql,
            'xls_to_sql': DatabaseConverter.excel_to_sql,
            'parquet_to_csv': DatabaseConverter.parquet_to_csv,
            'avro_to_json': DatabaseConverter.avro_to_json,
        }
        
        converter_func = converters.get(conversion_key)
        if converter_func:
            return await converter_func(input_path, output_path)
        
        raise NotImplementedError(f"Conversion from {source_format} to {target_format} not supported")
    
    @staticmethod
    async def sql_to_csv(input_path: str, output_path: str) -> str:
        """Convert SQL dump to CSV"""
        # Simple SQL INSERT parser
        with open(input_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Extract INSERT statements (simplified)
        import re
        insert_pattern = r"INSERT INTO \w+ \([^)]+\) VALUES \(([^)]+)\)"
        matches = re.findall(insert_pattern, sql_content)
        
        if not matches:
            raise ValueError("No INSERT statements found in SQL file")
        
        # Parse values
        rows = []
        for match in matches:
            values = [v.strip().strip("'\"") for v in match.split(',')]
            rows.append(values)
        
        # Write to CSV
        df = pd.DataFrame(rows)
        df.to_csv(output_path, index=False, header=False)
        
        return output_path
    
    @staticmethod
    async def csv_to_sql(input_path: str, output_path: str, table_name: str = 'data') -> str:
        """Convert CSV to SQL INSERT statements"""
        df = pd.read_csv(input_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write CREATE TABLE statement
            columns = ', '.join([f'{col} VARCHAR(255)' for col in df.columns])
            f.write(f"CREATE TABLE {table_name} ({columns});\n\n")
            
            # Write INSERT statements
            for _, row in df.iterrows():
                values = ', '.join([f"'{str(v)}'" for v in row.values])
                f.write(f"INSERT INTO {table_name} VALUES ({values});\n")
        
        return output_path
    
    @staticmethod
    async def json_to_sql(input_path: str, output_path: str, table_name: str = 'data') -> str:
        """Convert JSON to SQL INSERT statements"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            data = [data]
        
        df = pd.DataFrame(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write CREATE TABLE statement
            columns = ', '.join([f'{col} VARCHAR(255)' for col in df.columns])
            f.write(f"CREATE TABLE {table_name} ({columns});\n\n")
            
            # Write INSERT statements
            for _, row in df.iterrows():
                values = ', '.join([f"'{str(v)}'" for v in row.values])
                f.write(f"INSERT INTO {table_name} VALUES ({values});\n")
        
        return output_path
    
    @staticmethod
    async def excel_to_sql(input_path: str, output_path: str, table_name: str = 'data') -> str:
        """Convert Excel to SQL INSERT statements"""
        df = pd.read_excel(input_path)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write CREATE TABLE statement
            columns = ', '.join([f'{col} VARCHAR(255)' for col in df.columns])
            f.write(f"CREATE TABLE {table_name} ({columns});\n\n")
            
            # Write INSERT statements
            for _, row in df.iterrows():
                values = ', '.join([f"'{str(v)}'" for v in row.values])
                f.write(f"INSERT INTO {table_name} VALUES ({values});\n")
        
        return output_path
    
    @staticmethod
    async def parquet_to_csv(input_path: str, output_path: str) -> str:
        """Convert Parquet to CSV"""
        if not PYARROW_AVAILABLE:
            raise NotImplementedError("pyarrow not available")
        
        table = pq.read_table(input_path)
        df = table.to_pandas()
        df.to_csv(output_path, index=False)
        
        return output_path
    
    @staticmethod
    async def avro_to_json(input_path: str, output_path: str) -> str:
        """Convert Avro to JSON"""
        if not AVRO_AVAILABLE:
            raise NotImplementedError("avro not available")
        
        records = []
        with open(input_path, 'rb') as f:
            reader = DataFileReader(f, DatumReader())
            for record in reader:
                records.append(record)
            reader.close()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        
        return output_path
