import typer

def convert(full_file_path = typer.Argument(..., help = "The path to the Swissquote CSV exported from Swissquote portfolio"), sep = typer.Argument(...,help="The separator to be used in output csv.")):
    # run by command
    # python3 convert.py "/Users/teskesin/SynologyDrive/Code/git_clones/swissquote-to-parqet-csv-converter/transactions-from-08022019-to-05042023.csv" ";"
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
    
    mapping_cash_col = {'Datum':'datetime',
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
    
    
    mapping_cash_transactions = {'Dividende':'TransferIn',
                        'Kauf':'TransferOut', 
                        'Rückzahlung':'TransferIn', 
                        'Depotgebühren':'TransferOut',
                        'Fx-Gutschrift Comp.':'TransferIn', 
                        'Fx-Belastung Comp.':'TransferOut', 
                        'Spin off':'Spin off',
                        'Capital Gain':'TransferIn', 
                        'Verkauf':'TransferIn', 
                        'Forex-Gutschrift':'TransferIn', 
                        'Forex-Belastung':'TransferOut',
                        'Zins':'TransferIn',
                        'Interne Titelumbuchung':'Interne Titelumbuchung',
                        'Vergütung':'TransferIn',
                        'Berichtigung Börsengeb.':'Berichtigung Börsengeb.'}
    
    keep_columns = ['datetime',
               'type',
               'isin',
               'shares',
               'price',
               'fee',
               'Nettobetrag',
               'originalcurrency']
    
    exp = imp.rename(columns=mapping_col)[keep_columns]
    exp.replace(to_replace = mapping_cash_transactions.keys(), value = mapping_cash_transactions.values(), inplace = True)
    exp['holding'] = ''

    exp.query("type in ['TransferIn','TransferOut'] and originalcurrency == 'CHF'").holding
    # exp.loc[((exp.type == 'TransferIn')|(exp.type == 'TransferOut')) & (exp.originalcurrency == 'CHF'),'holding'] = 'hld_62fe9bf476362ac5e8b88ed5'
    # exp.loc[((exp.type == 'TransferIn')|(exp.type == 'TransferOut')) & (exp.originalcurrency == 'USD'),'holding'] = 'hld_62fe9c0476362ac5e8b88ed8' # USD
    # exp.loc[((exp.type == 'TransferIn')|(exp.type == 'TransferOut')) & (exp.originalcurrency == 'EUR'),'holding'] = 'hld_62fe9c1398683c34ff685ac2' # EUR

    exp.loc[ (exp.originalcurrency == 'CHF'),'holding'] = 'hld_6430515e76a945185e9a096b'
    exp.loc[ (exp.originalcurrency == 'USD'),'holding'] = 'hld_64305193646385c63825ecc0' # USD
    exp.loc[ (exp.originalcurrency == 'EUR'),'holding'] = 'hld_643051de76a945185e9a096f' # EUR


    exp['datetime'] = pd.to_datetime(exp['datetime'], format='%d-%m-%Y %H:%M:%S')
    exp['datetime'] = exp["datetime"].dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    exp['currency'] = exp['originalcurrency']
    exp['tax'] = 0.0
    port = exp[exp['type'].isin(['Buy','Sell','Dividend','TransferIn','TransferOut'])]
    cash = exp
    
    cash.replace(to_replace = mapping_transactions.keys(), value = mapping_transactions.values(), inplace = True)
    cash = cash[['datetime','type','Nettobetrag','currency','fee','holding','tax']]
    cash = cash[cash['type'].isin(['TransferIn','TransferOut'])]
    cash.rename(columns={'Nettobetrag':'amount'},inplace=True)
    cash['fee'] = 0
    cash['tax'] = 0
    
    cash['price'] = cash.amount.str.replace("-","") # if amount is string
    #cash['price'] = abs(cash.amount) # if amount is string
    cash['date'] = pd.to_datetime(cash['datetime']).dt.date
    cash['time'] = ""
    cash['shares'] = 1
    cash = cash[['datetime','price','shares','currency','tax','fee','type','holding']]
    
    file_out = './cash.csv'
    cash.to_csv(file_out,sep=';', index = False)
    #file_data = open(file_out, 'rb').read()
    #open(file_out, 'wb').write(file_data[:-2])
    
    exp.to_csv('./portfolio.csv',sep=';')
    


if __name__ == "__main__":
        #Calls the main function with CLI arguments
        typer.run(convert)