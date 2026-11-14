import { useState, useEffect } from 'react'
import './App.css'
import Packages from './components/Packages.jsx'

const API_URL = "http://127.0.0.1:8001"

function App() {
  const [packages, setPackages] = useState([])
  const [token, setToken] = useState("")

  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")

  useEffect(() => {
    fetch(API_URL + "/filtered_packages")
      .then((response) => response.json())
      .then((data) => setPackages(data));
  }, []);

  function handleLogin(e) {
    e.preventDefault();
    fetch(API_URL + "/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: username, password: password })
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.access_token) {
          setToken(data.access_token);
          alert("Logged in successfully!");
        } else {
          alert("Login failed");
        }
      });
  }

  return (
    <>
      <h1>Warehouse Management</h1>

      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <label>Username:
          <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
        </label>
        <label>Password:
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        <button type="submit">Login</button>
      </form>

      <hr />

      <Packages packages={packages} setPackages={setPackages} />
    </>
  )
}

export default App