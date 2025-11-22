import pandas as pd
import os
from datetime import datetime


class DataExporter:
    """Handles data export to various formats."""
    
    def export_to_excel(self, data, filepath):
        """
        Export scraped data to Excel file.
        
        Args:
            data (list): List of dictionaries containing business data
            filepath (str): Full path to save the file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Define expected columns
            expected_cols = [
                'Business Name', 'Category', 'Phone', 'Email', 
                'Website', 'Address', 'Rating', 'Reviews', 
                'Keyword', 'City'
            ]

            if not data:
                print("No data to export - creating empty file with headers")
                df_unique = pd.DataFrame(columns=expected_cols)
            else:
                # Create DataFrame
                df = pd.DataFrame(data)
                
                # Remove duplicates
                if 'Business Name' in df.columns and 'Address' in df.columns:
                    df_unique = df.drop_duplicates(subset=['Business Name', 'Address'], keep='first')
                else:
                    df_unique = df
                
                # Only select columns that exist in the data
                existing_cols = [col for col in expected_cols if col in df_unique.columns]
                # Add any extra columns that were scraped but not in expected list
                extra_cols = [col for col in df_unique.columns if col not in expected_cols]
                
                final_cols = existing_cols + extra_cols
                df_unique = df_unique[final_cols]
            
            # Export to Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df_unique.to_excel(writer, index=False, sheet_name='Results')
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Results']
                for idx, col in enumerate(df_unique.columns):
                    # For empty dataframe, use column name length
                    if df_unique.empty:
                        max_length = len(col)
                    else:
                        max_length = max(
                            df_unique[col].astype(str).apply(len).max(),
                            len(col)
                        )
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
            
            print(f"[SUCCESS] Data exported to: {filepath}")
            return True
            
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            return False
