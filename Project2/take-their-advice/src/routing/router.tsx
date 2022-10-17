import { createBrowserRouter } from 'react-router-dom';
import { ErrorPage } from '../pages/ErrorPage';
import { LoginPage } from '../pages/LoginPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <LoginPage />,
    errorElement: <ErrorPage />,
  },
]);
