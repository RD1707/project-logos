import Hero from '../components/home/Hero';
import Competencias from '../components/home/Competencias';
import ComoFunciona from '../components/home/ComoFunciona';

export default function Home() {
  return (
    <div className="min-h-screen">
      <Hero />
      <Competencias />
      <ComoFunciona />
    </div>
  );
}
