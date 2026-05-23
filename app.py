from flask import Flask, render_template, request, session, redirect, url_for
import datetime
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'rkstudio_secret_key'

ADMIN_PASSWORD = 'admin123'

def read_messages():
    messages = []
    if not os.path.exists('messages.txt'):
        return messages
    with open('messages.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    entries = content.strip().split('=' * 50)
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        msg = {}
        for line in entry.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_').replace('&', 'and')
                msg[key] = value.strip()
        if msg:
            messages.append({
                'time'   : msg.get('date___time', ''),
                'name'   : msg.get('name', ''),
                'phone'  : msg.get('phone', ''),
                'email'  : msg.get('email', ''),
                'service': msg.get('service', ''),
                'message': msg.get('message', '')
            })
    return messages

def read_orders():
    orders = []
    if not os.path.exists('orders.txt'):
        return orders
    with open('orders.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    entries = content.strip().split('=' * 50)
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        order = {}
        for line in entry.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                order[key] = value.strip()
        if order:
            orders.append({
                'time'        : order.get('date_&_time', ''),
                'service'     : order.get('service', ''),
                'name'        : order.get('name', ''),
                'phone'       : order.get('phone', ''),
                'quantity'    : order.get('quantity', ''),
                'size'        : order.get('size', ''),
                'design'      : order.get('design_details', ''),
                'address'     : order.get('delivery_address', ''),
                'instructions': order.get('special_instructions', '')
            })
    return orders

def read_bookings():
    bookings = []
    if not os.path.exists('bookings.txt'):
        return bookings
    with open('bookings.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    entries = content.strip().split('=' * 50)
    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
        booking = {}
        for line in entry.strip().split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                booking[key] = value.strip()
        if booking:
            bookings.append({
                'time'        : booking.get('date_&_time', ''),
                'name'        : booking.get('name', ''),
                'phone'       : booking.get('phone', ''),
                'package'     : booking.get('package', ''),
                'addons'      : booking.get('add-ons', ''),
                'custom'      : booking.get('custom_services', ''),
                'event_date'  : booking.get('event_date', ''),
                'event_type'  : booking.get('event_type', ''),
                'venue'       : booking.get('venue', ''),
                'guests'      : booking.get('expected_guests', ''),
                'requirements': booking.get('special_requirements', '')
            })
    return bookings

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/wedding')
def wedding():
    return render_template('wedding.html')

@app.route('/printing')
def printing():
    return render_template('printing.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name         = request.form.get('name', '')
        phone        = request.form.get('phone', '')
        package      = request.form.get('package', 'None')
        addons       = ', '.join(request.form.getlist('addons')) or 'None'
        custom       = ', '.join(request.form.getlist('custom')) or 'None'
        event_date   = request.form.get('event_date', '')
        event_type   = request.form.get('event_type', '')
        venue        = request.form.get('venue', '')
        guests       = request.form.get('guests', 'Not specified')
        requirements = request.form.get('requirements', '')
        time         = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open('bookings.txt', 'a', encoding='utf-8') as f:
            f.write("=" * 50 + "\n")
            f.write(f"Date & Time          : {time}\n")
            f.write(f"Name                 : {name}\n")
            f.write(f"Phone                : {phone}\n")
            f.write(f"Package              : {package}\n")
            f.write(f"Add-ons              : {addons}\n")
            f.write(f"Custom Services      : {custom}\n")
            f.write(f"Event Date           : {event_date}\n")
            f.write(f"Event Type           : {event_type}\n")
            f.write(f"Venue                : {venue}\n")
            f.write(f"Expected Guests      : {guests}\n")
            f.write(f"Special Requirements : {requirements}\n")
            f.write("=" * 50 + "\n\n")

        return render_template('booking.html', success=True)
    return render_template('booking.html', success=False)

@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        service      = request.form['service']
        name         = request.form['name']
        phone        = request.form['phone']
        quantity     = request.form['quantity']
        size         = request.form['size']
        design       = request.form['design']
        address      = request.form['address']
        instructions = request.form['instructions']
        time         = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open('orders.txt', 'a', encoding='utf-8') as f:
            f.write("=" * 50 + "\n")
            f.write(f"Date & Time          : {time}\n")
            f.write(f"Service              : {service}\n")
            f.write(f"Name                 : {name}\n")
            f.write(f"Phone                : {phone}\n")
            f.write(f"Quantity             : {quantity}\n")
            f.write(f"Size                 : {size}\n")
            f.write(f"Design Details       : {design}\n")
            f.write(f"Delivery Address     : {address}\n")
            f.write(f"Special Instructions : {instructions}\n")
            f.write("=" * 50 + "\n\n")

        return render_template('order.html', success=True, service=service)

    service = request.args.get('service', 'Printing Service')
    return render_template('order.html', success=False, service=service)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name    = request.form['name']
        phone   = request.form['phone']
        email   = request.form['email']
        service = request.form['service']
        message = request.form['message']
        time    = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open('messages.txt', 'a', encoding='utf-8') as f:
            f.write("=" * 50 + "\n")
            f.write(f"Date & Time : {time}\n")
            f.write(f"Name        : {name}\n")
            f.write(f"Phone       : {phone}\n")
            f.write(f"Email       : {email}\n")
            f.write(f"Service     : {service}\n")
            f.write(f"Message     : {message}\n")
            f.write("=" * 50 + "\n\n")

        return render_template('contact.html', success=True)
    return render_template('contact.html', success=False)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form['password']
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('admin.html', logged_in=False, error=True, messages=[], orders=[], bookings=[])
    if session.get('logged_in'):
        messages = read_messages()
        orders   = read_orders()
        bookings = read_bookings()
        return render_template('admin.html', logged_in=True, error=False, messages=messages, orders=orders, bookings=bookings)
    return render_template('admin.html', logged_in=False, error=False, messages=[], orders=[], bookings=[])

if __name__ == '__main__':
    app.run(debug=True)