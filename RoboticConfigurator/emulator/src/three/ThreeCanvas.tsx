/* eslint-disable @typescript-eslint/no-explicit-any */
import { useRef, useState } from 'react';

import { OrbitControls, Plane, Line } from '@react-three/drei';
import { Canvas, ThreeElements, useFrame } from '@react-three/fiber';

function Cube(props: ThreeElements['mesh']) {
  const ref = useRef<THREE.Mesh | null>(null);

  const [hovered, hover] = useState(false);
  const [clicked, click] = useState(false);

  useFrame(() => (ref.current != null ? (ref.current.rotation.x += 0.01) : null));

  return (
    <mesh
      {...props}
      ref={ref}
      scale={clicked ? 1.5 : 1}
      onClick={() => click(!clicked)}
      onPointerOver={() => hover(true)}
      onPointerOut={() => hover(false)}
    >
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color={hovered ? 'hotpink' : 'orange'} />
    </mesh>
  );
}

export function ThreeCanvas() {
  return (
    <Canvas>
      <hemisphereLight intensity={1} />
      <spotLight position={[5, 5, 5]} penumbra={1} intensity={1} />
      <OrbitControls makeDefault />
      <Plane args={[200, 200]} rotation={[90, 0, 0]} />
      <Line
        points={[
          [0, 0, 0],
          [0, 100, 200],
        ]} // Array of points, Array<Vector3 | Vector2 | [number, number, number] | [number, number] | number>
        color="blue"
      />
      <Cube position={[-1.2, 0, 0]} />
      <Cube position={[1.2, 0, 0]} />
    </Canvas>
  );
}
