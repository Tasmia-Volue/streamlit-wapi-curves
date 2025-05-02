import pandas as pd

def find_mismatch(curve_data, curve_data_dev):
   df_prod = pd.DataFrame({
       'Timestamp': curve_data['points'].index,
       'Series': curve_data['points']['value']
   })

   df_dev = pd.DataFrame({
       'Timestamp': curve_data_dev['points'].index,
       'Series': curve_data_dev['points']['value']
   })


   diff = df_prod.compare(df_dev)
   diff.rename(columns={'self': 'Production', 'other': 'Development'}, inplace=True)

   return diff

