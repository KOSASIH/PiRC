import React from 'react';
import Joystick from 'react-joystick-component';

function Teleop({ ros }) {
  const sendVelocity = (data) => {
    if (ros) {
      const twist = new ROSLIB.Message({
        linear: { x: data.y * 1.0, y: 0, z: 0 },
        angular: { x: 0, y: 0, z: -data.x * 2.0 }
      });
      const cmdVel = new ROSLIB.Topic({
        ros: ros,
        name: '/cmd_vel',
        messageType: 'geometry_msgs/Twist'
      });
      cmdVel.publish(twist);
    }
  };

  return (
    <div className="space-y-4">
      <Joystick
        baseColor="gray"
        stickColor="orange"
        size={120}
        baseSize={140}
        onMove={sendVelocity}
        onStop={() => sendVelocity({ x: 0, y: 0 })}
      />
      
      {/* Gamepad support */}
      <div className="text-center p-4 bg-gray-700 rounded-lg">
        <p>🎮 Gamepad Connected: {navigator.getGamepads ? 'Yes' : 'No'}</p>
        <button className="bg-orange-500 px-4 py-2 rounded mt-2">
          Connect Gamepad
        </button>
      </div>
    </div>
  );
}

export default Teleop;
