import React from 'react';
import {BrowserRouter, Routes, Route, Navigate} from 'react-router-dom';
import Home from './pages/Home';
import Route16 from './pages/Route16';




function App() {
  return (
    <>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="16" element={<Route16 />} />
        </Routes>
      </BrowserRouter>
    </>
  );
}

export default App;






// function App() {
//   const [data, setData] = useState(null);

//   useEffect(() => {
//     // Sprawdź poprawność URL-a
//     axios.get('http://localhost:8000/api/test-16/')
//       .then(response => {
//         // Sprawdź, czy odpowiedź zawiera dane
//         console.log(response.data);
//         setData(response.data);
//       })
//       .catch(error => {
//         console.error('There was an error fetching the data!', error);
//       });
//   }, []); // Pusty array [] jako drugi argument powoduje, że useEffect uruchamia się tylko raz

//   return (
//     <div>
//       <h1>Jak Pojadę</h1>
//       {data ? (
//         <div>
//           <p>Route ID: {data.route_id}</p>
//           <p>Route Short Name: {data.route_short_name}</p>
//           <p>Route Long Name: {data.route_long_name}</p>
//           <p>Route Description: {data.route_desc}</p>
//           <p>Route Type: {data.route_type}</p>
//           <p>Route Color: #{data.route_color}</p>
//           <p>Route Text Color: #{data.route_text_color}</p>
//         </div>
//       ) : (
//         <p>Loading...</p>
//       )}
//     </div>
//   );
// }

// export default App;