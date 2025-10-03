import { useState, useEffect } from 'react';

/**
 * Hook customizado para gerenciar estado no localStorage
 * @param {string} key - Chave do localStorage
 * @param {any} initialValue - Valor inicial
 * @returns {[any, Function]} - [valor, setter]
 */
export function useLocalStorage(key, initialValue) {
  // Estado para armazenar o valor
  const [storedValue, setStoredValue] = useState(() => {
    try {
      // Tentar obter do localStorage
      const item = window.localStorage.getItem(key);
      // Parse JSON ou retorna o valor inicial
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error(`Erro ao ler localStorage key "${key}":`, error);
      return initialValue;
    }
  });

  // Retorna uma versão wrappada da função setter que
  // persiste o novo valor no localStorage
  const setValue = (value) => {
    try {
      // Permite que value seja uma função para ter a mesma API do useState
      const valueToStore = value instanceof Function ? value(storedValue) : value;

      // Salvar estado
      setStoredValue(valueToStore);

      // Salvar no localStorage
      if (valueToStore === null || valueToStore === undefined) {
        window.localStorage.removeItem(key);
      } else {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.error(`Erro ao salvar localStorage key "${key}":`, error);
    }
  };

  // Sincronizar com mudanças no localStorage de outras tabs/windows
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === key && e.newValue !== null) {
        try {
          setStoredValue(JSON.parse(e.newValue));
        } catch (error) {
          console.error(`Erro ao sincronizar localStorage key "${key}":`, error);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, [key]);

  return [storedValue, setValue];
}
