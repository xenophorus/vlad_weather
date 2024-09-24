header = '''
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Document</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
<div class="container">
'''

bottom = "</div></body></html>"

def append_html(data):
    with open("icons.html", "a") as f:
        f.write(data)
        f.write("\n")


names = ["day", "night", "iday"]

append_html(header)

for i in range(100):
    for name in names:
        div = f'''
    <div class="box">
      <div>
        <span>{i}</span>  
      </div>
      <div>
        <img src="https://primpogoda.ru/img/forecast_icons/svg/icon_{str(i).rjust(2, "0")}_{name}.svg">
      </div>
    </div>'''
        append_html(div)

append_html(bottom)
