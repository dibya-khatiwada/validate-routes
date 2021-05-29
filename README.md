
***Work in progress***
-

### Validating BGP routes from PCH routes collectors
    - https://www.pch.net/resources/Routing_Data/ 
    - Using the source code at https://github.com/InternetHealthReport/route-origin-validator/

### Running program
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt

### Checking routes
    cd src/
    python checkroutes4.py
    python checkroutes6.py

    See sample output in example_output.txt
