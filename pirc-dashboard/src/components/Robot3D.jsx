import React, { useRef, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';

function RobotModel({ ros, robotId }) {
  const group = useRef();
  const [pose, setPose] = useState({ x: 0, y: 0, z: 0, yaw: 0 });

  useEffect(() => {
    if (ros) {
      const poseSub = new ROSLIB.Topic({
        ros: ros,
        name: `/robot/${robotId}/pose`,
        messageType: 'geometry_msgs/PoseStamped'
      });
      poseSub.subscribe((msg) => {
        setPose({
          x: msg.pose.position.x,
          y: msg.pose.position.y,
          z: msg.pose.position.z,
          yaw: 2 * Math.atan2(msg.pose.orientation.z, msg.pose.orientation.w)
        });
      });
    }
  }, [ros, robotId]);

  useFrame(() => {
    if (group.current) {
      group.current.position.set(pose.x, pose.y, pose.z);
      group.current.rotation.z = pose.yaw;
    }
  });

  return (
    <group ref={group}>
      {/* Robot chassis */}
      <mesh>
        <boxGeometry args={[0.5, 0.1, 0.3]} />
        <meshStandardMaterial color="orange" />
      </mesh>
      {/* Wheels */}
      <mesh position={[-0.2, -0.1, 0.12]}>
        <cylinderGeometry args={[0.05, 0.05, 0.03]} />
        <meshStandardMaterial color="black" />
      </mesh>
      <mesh position={[0.2, -0.1, 0.12]}>
        <cylinderGeometry args={[0.05, 0.05, 0.03]} />
        <meshStandardMaterial color="black" />
      </mesh>
    </group>
  );
}

function Robot3D({ ros, robotId }) {
  return (
    <Canvas camera={{ position: [2, 2, 2], fov: 60 }}>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <RobotModel ros={ros} robotId={robotId} />
      <OrbitControls />
      <Stars />
      <gridHelper args={[10, 10]} />
    </Canvas>
  );
}

export default Robot3D;
