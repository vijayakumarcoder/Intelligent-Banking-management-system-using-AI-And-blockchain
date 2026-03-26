from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from blockchain import Blockchain
from wallet import Wallet
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this_in_production'  # Change this!

# Global blockchain instance
blockchain = Blockchain()

# Database setup
def init_db():
    """
    Database initialize pannum
    Users table create pannum
    """
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            public_key TEXT NOT NULL,
            private_key TEXT NOT NULL,
            wallet_address TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Helper function - password hash pannum
def hash_password(password):
    """
    Password ah SHA-256 use panni hash pannum
    """
    return hashlib.sha256(password.encode()).hexdigest()

# Helper function - user wallet address get pannum
def get_user_wallet(username):
    """
    Username ah use panni wallet details edukrom
    """
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT wallet_address, private_key, public_key FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'address': result[0],
            'private_key': result[1],
            'public_key': result[2]
        }
    return None

# Routes

@app.route('/')
def index():
    """
    Home page - login redirect pannum
    """
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration
    - Username, password get pannum
    - Wallet keys generate pannum
    - Database la store pannum
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Wallet generate pannum
        wallet = Wallet()
        keys = wallet.generate_keys()
        
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (username, password, public_key, private_key, wallet_address)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                username,
                hash_password(password),
                keys['public_key'],
                keys['private_key'],
                keys['address']
            ))
            
            conn.commit()
            conn.close()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        
        except sqlite3.IntegrityError:
            flash('Username already exists!', 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login
    - Username, password verify pannum
    - Session create pannum
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                      (username, hash_password(password)))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """
    User dashboard
    - Balance kaatum
    - Wallet details kaatum
    """
    if 'username' not in session:
        return redirect(url_for('login'))
    
    wallet = get_user_wallet(session['username'])
    balance = blockchain.get_balance(wallet['address'])
    
    return render_template('dashboard.html',
                         username=session['username'],
                         wallet_address=wallet['address'],
                         balance=balance,
                         blockchain_length=len(blockchain.chain))

@app.route('/send', methods=['GET', 'POST'])
def send_money():
    """
    Money send pannum
    - Receiver address, amount get pannum
    - Transaction sign pannum
    - Blockchain la add pannum
    """
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        receiver = request.form['receiver']
        amount = float(request.form['amount'])
        fee = 0.1  # Transaction fee

        wallet = get_user_wallet(session['username'])
        sender_balance = blockchain.get_balance(wallet['address'])

        # Balance check pannum (including fee)
        if amount + fee > sender_balance:
            flash('Insufficient balance! (including transaction fee)', 'danger')
            return redirect(url_for('send_money'))

        # AI Fraud detection
        if blockchain.check_fraud(amount, sender_balance):
            flash('Transaction flagged as suspicious! Please contact support.', 'warning')
            return redirect(url_for('send_money'))

        # Transaction data prepare pannum
        transaction_data = {
            'sender': wallet['address'],
            'receiver': receiver,
            'amount': amount
        }
        
        # Transaction sign pannum
        wallet_obj = Wallet()
        signature = wallet_obj.sign_transaction(transaction_data, wallet['private_key'])
        
        if signature:
            # Blockchain la transaction add pannum
            blockchain.add_transaction(
                wallet['address'],
                receiver,
                amount,
                signature,
                fee
            )

            # Add to AI training data
            hour = datetime.now().hour
            blockchain.transaction_features.append([amount, hour])

            # Mining pannum (production la separate process ah irukkum)
            blockchain.mine_pending_transactions(wallet['address'])

            flash(f'Successfully sent {amount} coins to {receiver}! (Fee: {fee} BC)', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Transaction signing failed!', 'danger')
            return redirect(url_for('send_money'))
    
    wallet = get_user_wallet(session['username'])
    balance = blockchain.get_balance(wallet['address'])
    
    return render_template('send.html', balance=balance)

@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    """
    Deposit money to wallet
    """
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        amount = float(request.form['amount'])
        if amount <= 0:
            flash('Invalid amount!', 'danger')
            return redirect(url_for('deposit'))

        wallet = get_user_wallet(session['username'])
        blockchain.deposit(wallet['address'], amount)
        flash(f'Successfully deposited {amount} BC!', 'success')
        return redirect(url_for('dashboard'))

    wallet = get_user_wallet(session['username'])
    balance = blockchain.get_balance(wallet['address'])

    return render_template('deposit.html', balance=balance)

@app.route('/history')
def transaction_history():
    """
    Transaction history kaatum
    - User oda all transactions fetch pannum
    """
    if 'username' not in session:
        return redirect(url_for('login'))

    wallet = get_user_wallet(session['username'])
    transactions = blockchain.get_transactions_for_address(wallet['address'])
    balance = blockchain.get_balance(wallet['address'])

    return render_template('history.html',
                         transactions=transactions,
                         wallet_address=wallet['address'],
                         username=session['username'],
                         balance=balance)

@app.route('/blockchain')
def view_blockchain():
    """
    Full blockchain view pannum (JSON format)
    """
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return jsonify({
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
        'valid': blockchain.is_chain_valid()
    })

@app.route('/logout')
def logout():
    """
    User logout pannum
    Session clear pannum
    """
    session.pop('username', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

# Initialize database on first run
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000)