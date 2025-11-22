from data.exporter import DataExporter
import os

def test_empty_export():
    exporter = DataExporter()
    filepath = os.path.abspath("test_empty.xlsx")
    
    # Clean up if exists
    if os.path.exists(filepath):
        os.remove(filepath)
        
    print(f"Attempting to export empty list to {filepath}...")
    result = exporter.export_to_excel([], filepath)
    
    print(f"Result: {result}")
    
    if os.path.exists(filepath):
        print("File WAS created.")
    else:
        print("File was NOT created.")

if __name__ == "__main__":
    test_empty_export()
