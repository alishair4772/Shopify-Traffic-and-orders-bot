import threading
import pandas as pd
from main import shopifyStores

urls = []

df = pd.read_csv("input.csv")
for index, row in df.iterrows():
    urls.append(row)

threads = []
for i in urls:
    for k in range(1,i['browsers']+1):
        thread = threading.Thread(target=shopifyStores, args=(i['proxy file'],i['visitors'],i['products'],i['minimum sale'],i['maximum sale'],i['hours'],))
        thread.start()
        threads.append(thread)
for j in threads:
    j.join()