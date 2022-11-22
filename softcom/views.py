from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.conf.urls.static import static
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import base64
from io import BytesIO
from sklearn import metrics
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report


# Create your views here.
def index(request):
    # request.session.clear()
    if bool(request.FILES.get('document', False)) == True:
        uploaded_file = request.FILES['document']
        name = uploaded_file.name
        request.session['name'] = name
        df = pd.read_csv(uploaded_file)
        dataFrame = df.to_json()
        request.session['df'] = dataFrame
        
        rows = len(df.index)
        request.session['rows'] = rows
        header = df.axes[1].values.tolist()
        request.session['header'] = header
        
        attributes = len(header)
        types = []
        maxs = []
        mins = []
        means = []
        # statistic attribut
        for i in range(len(header)):
            types.append(df[header[i]].dtypes)
            if df[header[i]].dtypes != 'object':
                maxs.append(df[header[i]].max())
                mins.append(df[header[i]].min())
                means.append(round(df[header[i]].mean(),2))
            else:
                maxs.append(0)
                mins.append(0)
                means.append(0)

        zipped_data = zip(header, types, maxs, mins, means)
        print(maxs)
        datas = df.values.tolist()
        data ={  
                "header": header,
                "headers": json.dumps(header),
                "name": name,
                "attributes": attributes,
                "rows": rows,
                "zipped_data": zipped_data,
                'df': datas,
                "type": types,
                "maxs": maxs,
                "mins": mins,
                "means": means,
            }
    else:
        name = 'None'
        attributes = 'None'
        rows = 'None'
        data ={
                "name": name,
                "attributes": attributes,
                "rows": rows,
            }
    return render(request, 'index.html', data) 

def checker_page(request):
    if request.POST:
        drop_header = request.POST.getlist('drop_header')
        print(drop_header)
        for head in drop_header:
            print(head)
        request.session['drop'] = drop_header
        method = request.POST.get('selected_method')
        if method == '1':
            return redirect('classification')
        elif method == '2':
            return redirect('clustering')
        else: 
            return redirect('preprocessing')
    else:
        return render(request, 'index.html')

def chooseMethod(request):
    if request.method == 'POST':
        method = request.POST.get('method')
        print('method di session : ', method)
        request.session['method'] = method
    return redirect('classification')

def clustering(request):
    rows = request.session['rows']
    name = request.session['name']
    df = request.session['df']
    df = pd.read_json(df)
    print(df)
    features = request.session['drop']
    print(features)
    nilai_x = features[0]
    nilai_y = features[1]
    if request.method == 'POST' and request.POST['nilai_k']:
        k = request.POST['nilai_k']
        nilai_k = int(k)

        x_array = np.array(df.iloc[:, 3:5])

        scaler = MinMaxScaler()
        x_scaled = scaler.fit_transform(x_array)

        # Menentukan dan mengkonfigurasi fungsi kmeans
        kmeans = KMeans(n_clusters = nilai_k)
        # Menentukan kluster dari data
        kmeans.fit(x_scaled)

        # Menambahkan kolom "kluster" dalam data frame
        df['cluster'] = kmeans.labels_
        cluster = df['cluster'].value_counts()
        clusters = cluster.to_dict()
        sort_cluster = []
        label = []
        for i in sorted(clusters):
            sort_cluster.append(clusters[i])
            label.append(i)
        
        fig, ax = plt.subplots()
        sct = ax.scatter(x_scaled[:,1], x_scaled[:,0], s = 200, c = df.cluster)
        legend1 = ax.legend(*sct.legend_elements(),loc="lower left", title="Clusters")
        ax.add_artist(legend1)
        centers = kmeans.cluster_centers_
        ax.scatter(centers[:,1], centers[:,0], c='red', s=200)
        plt.title("Clustering K-Means Results")
        plt.xlabel(nilai_x)
        plt.ylabel(nilai_y)
        graph = get_graph()

        if name:
            data = {
                "name": name,
                "clusters": sort_cluster,
                "rows": rows,
                "features": features,
                "label": label,
                "chart": graph,
            }
    else:
        data = {
            "name": '',
        }

    return render(request, 'clustering.html', data) 

def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph