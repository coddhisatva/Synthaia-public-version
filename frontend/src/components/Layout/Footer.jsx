export default function Footer() {
  return (
    <footer className="bg-gray-800 text-gray-300 mt-auto">
      <div className="container mx-auto px-4 py-6 text-center">
        <p className="text-sm">
          Synthaia &copy; {new Date().getFullYear()} - AI Music Toolkit
        </p>
      </div>
    </footer>
  );
}

