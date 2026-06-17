import { createContext, useState } from "react";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("access_token"));
  const [username, setUsername] = useState(() => localStorage.getItem("username"));

  const isAuthenticated = !!token;

  const login = (accessToken, user) => {
    setToken(accessToken);
    setUsername(user);
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("username", user);
  };

  const logout = () => {
    setToken(null);
    setUsername(null);
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
  };

  return (
    <AuthContext.Provider value={{ token, username, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
