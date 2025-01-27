#create virtual environment
python -m venv env


# powershell (run as adminstator)only once after installation of python
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned 

#activate virtual environment
env/Scripts/activate

#install package from requirement.txt
pip install -r requirement.txt

#dowload dataset
python -m nltk.downloader popular
#check
pip list

#run app
 flask --app app run