import tempfile

def save_uploaded_file(uploaded_file):
    
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_path = temp_file.name

    return temp_path