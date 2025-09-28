import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

import Chat from './pages/chat';

const App: React.FC = () => {
  return (
    <Router>
      <Routes>
        <Route path="*" element={ <Chat />} />
      </Routes>
    </Router>
  );
};

export default App;

