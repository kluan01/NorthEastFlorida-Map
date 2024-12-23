const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer>
      <p>&copy; Luangsouphom & Parekh {currentYear}</p>
    </footer>
  );
};

export default Footer;
