from flask import Flask, render_template, request

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/wedding')
def wedding():
    return render_template('wedding.html')

@app.route('/printing')
def printing():
    return render_template('printing.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        service = request.form['service']
        message = request.form['message']
        print(f"New Message from: {name} | Phone: {phone} | Email: {email} | Service: {service} | Message: {message}")
        return render_template('contact.html', success=True)
    return render_template('contact.html', success=False)

if __name__ == '__main__':
    app.run(debug=True)