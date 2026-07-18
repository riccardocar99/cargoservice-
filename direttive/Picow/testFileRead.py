def get_html(html_name, distance):
    # open html_name (index.html), 'r' = read-only as variable 'file'
    print("file read")
    with open(html_name, 'r') as file:
        html    = file.read()
    #content = html.replace("<h2 id=\"ultrasonic\"></h2>", f"<h2 id=\"ultrasonic\">{distance}cm</h2>")
    print(html)
    #return html

get_html('idexSonar.html', 10)