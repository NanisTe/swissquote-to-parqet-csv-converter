import typer

def convert(full_file_path = typer.Argument(..., help = "The path to the Swissquote CSV exported from Swissquote portfolio"), sep = typer.Argument(...,help="The separator to be used in output csv.")):
    # 
    import pandas as pd
    import os
    
    filename = os.path.basename(full_file_path)
    dirname = os.path.dirname(full_file_path)
    
    imp = pd.read_csv(dirname+'/'+filename,sep = ';')
    
    mapping_col = {'Datum':'datetime',
               'Auftrag #':'Auftrag #',
               'Transaktionen':'type',
               'Symbol':'Symbol',
               'Name':'Name',
               'ISIN':'isin',
               'Anzahl':'shares',
               'Stückpreis':'price', 
               'Kosten':'fee', 
               'Aufgelaufene Zinsen':'Aufgelaufene Zinsen', 
               'Nettobetrag':'Nettobetrag',
               'Saldo':'Saldo',
               'Währung':'originalcurrency'}

    mapping_transactions = {'Dividende':'Dividend',
                        'Kauf':'Buy', 
                        'Rückzahlung':'Rückzahlung', 
                        'Depotgebühren':'Depotgebühren',
                        'Fx-Gutschrift Comp.':'TransferIn', 
                        'Fx-Belastung Comp.':'TransferOut', 
                        'Spin off':'Spin off',
                        'Capital Gain':'Capital Gain', 
                        'Verkauf':'Sell', 
                        'Forex-Gutschrift':'Forex-Gutschrift', 
                        'Forex-Belastung':'Forex-Belastung',
                        'Zins':'Zins',
                        'Interne Titelumbuchung':'Interne Titelumbuchung',
                        'Vergütung':'TransferIn',
                        'Berichtigung Börsengeb.':'Berichtigung Börsengeb.'}
    keep_columns = ['datetime',
               'type',
               'isin',
               'shares',
               'price',
               'fee',
               'originalcurrency']
    
    exp = imp.rename(columns=mapping_col)[keep_columns]
    exp.replace(to_replace = mapping_transactions.keys(), value = mapping_transactions.values(), inplace = True)
    exp['holding'] = ''

    exp.query("type in ['TransferIn','TransferOut'] and originalcurrency == 'CHF'").holding
    exp.loc[((exp.type == 'TransferIn')|(exp.type == 'TransferOut')) & (exp.originalcurrency == 'CHF'),'holding'] = 'hld_62fe9bf476362ac5e8b88ed5'
    exp.loc[((exp.type == 'TransferIn')|(exp.type == 'TransferOut')) & (exp.originalcurrency == 'USD'),'holding'] = 'hld_62fe9c0476362ac5e8b88ed8' # USD
    exp.loc[((exp.type == 'TransferIn')|(exp.type == 'TransferOut')) & (exp.originalcurrency == 'EUR'),'holding'] = 'hld_62fe9c1398683c34ff685ac2' # EUR

    exp['datetime'] = pd.to_datetime(exp['datetime'], format='%d-%m-%Y %H:%M:%S')
    exp['datetime'] = exp["datetime"].dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    exp['currency'] = exp['originalcurrency']
    exp['tax'] = 0.0
    port = exp[exp['type'].isin(['Buy','Sell','Dividend','TransferIn','TransferOut'])]
    cash = exp[exp['type'].isin(['TransferIn','TransferOut'])][['datetime','type','shares','price','fee','holding','tax']]

    cash.to_csv(dirname+'/cash.csv',sep=';', index = False)

    exp.to_csv(dirname+'/portfolio.csv',sep=';', index = False)
    


if __name__ == "__main__":
        #Calls the main function with CLI arguments
        typer.run(convert)