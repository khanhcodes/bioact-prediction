import streamlit as st 
import pandas as pd
from PIL import Image
import subprocess
import os
import base64
import pickle

#Molecular descriptor calculator
def desc_cal():
    command = 'java -Xms1G -Xmx1G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv'
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    os.remove('molecule.smi')

#File download
def file_download(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    html = '<a download="predictions.csv" href="data:file/csv;base64,{b64}"> Download Predictions </a>'
    return html

#Model Building
def build_model(input_data):
    load_model = pickle.load(open('acetylcholinesterase_model.pkl', 'rb'))
    prediction = load_model.predict(input_data)
    st.header('**🎉 Prediction output**')
    prediction_output = pd.Series(prediction, name='pIC50')
    molecule_name = pd.Series(load_data[1], name ='molecule_name')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    st.write(df)
    st.markdown(file_download(df), unsafe_allow_html=True)

#Logo 
image = Image.open('logo.png')
st.image(image, use_column_width=True)

#Title
st.markdown("""# 💊 Bioactivity Prediction App (Acetylcholinesterase)
This web application allows you to predict the bioactivity of interested compounds towards inhibiting the `Acetylcholinesterase` enzyme. `Acetylcholinesterase` is a drug target for Alzheimer's disease. 
Once you upload a CSV file containing canonical SMILES, the app will calculate the fingerprints for each molecule and return the predicted bioactivity data. This data is helpful in discovering drugs that have promising potential towards `Acetylcholinesterase` enzyme inhibition.  """)

#Sidebar
with st.sidebar.header('Upload your CSV data'):
    uploaded_file = st.sidebar.file_uploader("Upload your file",type=['txt'])
    st.sidebar.markdown("""[Example input file](https://github.com/khanhcodes/bioact-prediction/blob/main/example_acetylcholinesterase.txt)""")

if st.sidebar.button('Predict bioactivity data'):
    load_data = pd.read_table(uploaded_file, sep=' ', header=None)
    load_data.to_csv('molecule.smi', sep = '\t', header = False, index = False)

    st.header('**📄 Original Input Data**')
    st.write(load_data)
    
    with st.spinner('Wait a second. We are calculating the descriptors...'):
        desc_cal()

    st.header('**✔️ Calculated Molecular Descriptors**')
    desc = pd.read_csv('descriptors_output.csv')
    st.write(desc)
    st.write(desc.shape)

    #Return a list of descriptors without ChEMBL ID
    st.header('**✅ Subset of descriptors from previously built models (without ChEMBL ID)**')
    with st.spinner('Removing the low variance descriptors...'):
        desc_new = desc.drop(['Name'], axis = 1)
        desc_new = desc_new.fillna(desc_new.mean())
        Xlist = list(pd.read_csv('descriptor_list.csv').columns)
        subset = desc_new[Xlist]
        st.write(subset)
        st.write(subset.shape)
    
    # Apply trained model to make prediction on query compounds
    build_model(subset)
else:
    st.info('Upload input data in the sidebar to start predicting!')


