const express = require('express');
const { v4: uuidv4 } = require('uuid');

const app = express();
app.use(express.json());

const users = new Map();
const todos = new Map();
let authToken = null;

// HTML pages for UI tests
const loginHTML = `
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
  <form id="login-form">
    <input name="email" type="email" placeholder="Email" />
    <input name="password" type="password" placeholder="Password" />
    <button type="submit">Login</button>
  </form>
  <a href="/register">Register</a>
  <div class="error-message" style="display:none"></div>
</body>
</html>`;

const registerHTML = `
<!DOCTYPE html>
<html>
<head><title>Register</title></head>
<body>
  <form id="register-form">
    <input name="name" type="text" placeholder="Name" />
    <input name="email" type="email" placeholder="Email" />
    <input name="password" type="password" placeholder="Password" />
    <input name="confirmPassword" type="password" placeholder="Confirm Password" />
    <button type="submit">Register</button>
  </form>
  <a href="/login">Login</a>
  <div class="error-message" style="display:none"></div>
  <div class="success-message" style="display:none"></div>
</body>
</html>`;

const todosHTML = (todos = []) => `
<!DOCTYPE html>
<html>
<head><title>Todos</title></head>
<body>
  <h1>Todos</h1>
  <input placeholder="What needs to be done" id="new-todo" />
  <div class="todo-list">
    ${todos.map(t => `
      <div class="todo-item" data-id="${t.id}">
        <input type="checkbox" name="completed" ${t.completed ? 'checked' : ''} />
        <span>${t.title}</span>
        <button class="delete">×</button>
      </div>
    `).join('')}
  </div>
  <div class="filters">
    <button class="filter-all">All</button>
    <button class="filter-active">Active</button>
    <button class="filter-completed">Completed</button>
  </div>
  <button class="clear-completed">Clear completed</button>
  <div class="todo-count">${todos.length} items left</div>
  <div class="empty-state" style="display:${todos.length === 0 ? 'block' : 'none'}">No todos</div>
</body>
</html>`;

app.get('/login', (req, res) => res.send(loginHTML));
app.get('/register', (req, res) => res.send(registerHTML));
app.get('/todos', (req, res) => res.send(todosHTML(Array.from(todos.values()))));
app.get('/', (req, res) => res.send('<html><body><a href="/login">Login</a> | <a href="/todos">Todos</a></body></html>'));

app.post('/api/auth/register', (req, res) => {
  const { email, name, password } = req.body;
  if (!email || !name || !password) {
    return res.status(422).json({ message: 'Missing required fields' });
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return res.status(400).json({ message: 'Invalid email format' });
  }
  if (password.length < 8 || !/[A-Z]/.test(password) || !/[0-9]/.test(password)) {
    return res.status(400).json({ message: 'Password too weak' });
  }
  if (users.has(email)) {
    return res.status(400).json({ message: 'Email already exists' });
  }
  const user = { id: uuidv4(), email, name, password };
  users.set(email, user);
  const token = uuidv4();
  authToken = token;
  res.status(201).json({ token, user: { id: user.id, email: user.email, name: user.name } });
});

app.post('/api/auth/login', (req, res) => {
  const { email, password } = req.body;
  const user = users.get(email);
  if (!user || user.password !== password) {
    return res.status(401).json({ message: 'Invalid credentials' });
  }
  const token = uuidv4();
  authToken = token;
  res.json({ token, user: { id: user.id, email: user.email, name: user.name } });
});

app.get('/api/auth/me', (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ') || !authHeader.includes(' ')) {
    return res.status(401).json({ message: 'Unauthorized' });
  }
  res.json({ id: '1', email: 'test@test.com', name: 'Test User' });
});

app.get('/api/todos', (req, res) => {
  res.json({ todos: Array.from(todos.values()), total: todos.size, page: 1, limit: 10 });
});

app.post('/api/todos', (req, res) => {
  const { title, completed = false } = req.body;
  if (!title) {
    return res.status(400).json({ message: 'Title is required' });
  }
  const todo = { id: uuidv4(), title, completed, userId: '1', createdAt: new Date().toISOString() };
  todos.set(todo.id, todo);
  res.status(201).json(todo);
});

app.patch('/api/todos/:id', (req, res) => {
  const { id } = req.params;
  const todo = todos.get(id);
  if (!todo) {
    return res.status(404).json({ message: 'Todo not found' });
  }
  const updated = { ...todo, ...req.body, updatedAt: new Date().toISOString() };
  todos.set(id, updated);
  res.json(updated);
});

app.delete('/api/todos/:id', (req, res) => {
  const { id } = req.params;
  if (!todos.has(id)) {
    return res.status(404).json({ message: 'Todo not found' });
  }
  todos.delete(id);
  res.status(204).send();
});

app.post('/api/todos/:id/toggle', (req, res) => {
  const { id } = req.params;
  const todo = todos.get(id);
  if (!todo) {
    return res.status(404).json({ message: 'Todo not found' });
  }
  todo.completed = !todo.completed;
  todos.set(id, todo);
  res.json(todo);
});

app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.post('/api/users', (req, res) => {
  const { email, name, password } = req.body;
  if (!email || !name || !password) {
    return res.status(422).json({ message: 'Missing required fields' });
  }
  if (users.has(email)) {
    return res.status(400).json({ message: 'Email already exists' });
  }
  const user = { id: uuidv4(), email, name, createdAt: new Date().toISOString() };
  users.set(email, { ...user, password });
  res.status(201).json(user);
});

app.get('/api/users', (req, res) => {
  res.json({ users: Array.from(users.values()).map(u => ({ id: u.id, email: u.email, name: u.name })), total: users.size, page: 1, limit: 10 });
});

app.get('/api/users/:id', (req, res) => {
  const user = Array.from(users.values()).find(u => u.id === req.params.id);
  if (!user) return res.status(404).json({ message: 'User not found' });
  res.json({ id: user.id, email: user.email, name: user.name, createdAt: user.createdAt });
});

app.delete('/api/users/:id', (req, res) => {
  const user = Array.from(users.values()).find(u => u.id === req.params.id);
  if (!user) return res.status(404).json({ message: 'User not found' });
  users.delete(user.email);
  res.status(204).send();
});

const PORT = 3000;
app.listen(PORT, () => console.log(`Mock server running on http://localhost:${PORT}`));