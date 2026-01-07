import sys
import os
from datetime import datetime

# 1. Setup path to find 'models.py'
sys.path.insert(0, os.getcwd())

try:
    from models import Base
    # Force load all models
    import models 
except ImportError as e:
    print(f"[ERROR] Could not import Base/models: {e}")
    sys.exit(1)

def type_to_dbml(col_type):
    """Converts SQLAlchemy types to DBML string types"""
    return str(col_type).split('(')[0].lower()

def generate_dbml():
    output = []
    # Add a timestamp so you know it actually updated
    output.append(f"// Nu-age Backend Schema")
    output.append(f"// Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"Project Nu_age {{\n  database_type: 'PostgreSQL'\n}}\n")

    tables = Base.metadata.sorted_tables
    
    for table in tables:
        output.append(f"Table {table.name} {{")
        
        for col in table.columns:
            props = []
            if col.primary_key:
                props.append("pk")
            if col.autoincrement is True:
                props.append("increment")
            if not col.nullable:
                props.append("not null")
            if col.unique:
                props.append("unique")
            
            prop_str = f" [{', '.join(props)}]" if props else ""
            col_type = type_to_dbml(col.type)
            output.append(f"  {col.name} {col_type}{prop_str}")
        
        output.append("}\n")

    output.append("// Relationships")
    for table in tables:
        for fk in table.foreign_key_constraints:
            for fk_element in fk.elements:
                local_col = fk_element.parent.name
                remote_table = fk_element.column.table.name
                remote_col = fk_element.column.name
                
                output.append(f"Ref: {table.name}.{local_col} > {remote_table}.{remote_col}")

    # 'w' mode overwrites the existing file with new content
    with open("nu_age.dbml", "w") as f:
        f.write("\n".join(output))
    
    print(f"SUCCESS! Updated 'nu_age.dbml' at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    generate_dbml()