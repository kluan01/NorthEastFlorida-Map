import Header from "./Header";
import Footer from "./Footer";
import Content from "./Content";

function App() {
  return (
    <div className="App">
      <Header title="Northeast Florida Shortest Path Finder" />
      <main>
        <Content />
      </main>
      <Footer />
    </div>
  );
}

export default App;
