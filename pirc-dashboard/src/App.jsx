import React, { useEffect, useState } from 'react';
import Robot3D from './components/Robot3D';
import VideoStream from './components/VideoStream';
import Teleop from './components/Teleop';
import MissionPlanner from './components/MissionPlanner';
import FleetManager from './components/FleetManager';
import ARView from './components/ARView';
import { useROS } from './hooks/useROS';

function App() {
  const { ros, connected } = useROS('ws://localhost:9090');
  const [activeRobot, setActiveRobot] = useState('pirc-01');
  const [videoStream, setVideoStream] = useState(null);

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 p-4 shadow-lg">
        <div className="flex justify-between items-center max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold">🚀 PiRC Control Center</h1>
          <div className="flex space-x-4">
            <span className={`px-3 py-1 rounded-full text-sm ${
              connected ? 'bg-green-500' : 'bg-red-500'
            }`}>
              {connected ? '🟢 ROS Connected' : '🔴 Disconnected'}
            </span>
            <select 
              value={activeRobot} 
              onChange={(e) => setActiveRobot(e.target.value)}
              className="bg-gray-700 p-2 rounded"
            >
              <option value="pirc-01">PiRC-01</option>
              <option value="pirc-02">PiRC-02</option>
              <option value="pirc-fleet">Fleet</option>
            </select>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 3D Robot Viewer */}
        <div className="bg-gray-800 rounded-xl p-6">
          <h2 className="text-xl font-bold mb-4">3D Robot Viewer</h2>
          <Robot3D ros={ros} robotId={activeRobot} />
        </div>

        {/* Live Video + Teleop */}
        <div className="space-y-6">
          <div className="bg-gray-800 rounded-xl p-6">
            <h2 className="text-xl font-bold mb-4">Live Video 60FPS</h2>
            <VideoStream robotId={activeRobot} />
          </div>
          <div className="bg-gray-800 rounded-xl p-6">
            <h2 className="text-xl font-bold mb-4">Teleop Control</h2>
            <Teleop ros={ros} />
          </div>
        </div>

        {/* Mission Planner */}
        <div className="lg:col-span-2 bg-gray-800 rounded-xl p-6">
          <h2 className="text-xl font-bold mb-4">Mission Planner</h2>
          <MissionPlanner ros={ros} />
        </div>

        {/* Fleet Management + AR */}
        <div className="space-y-6 lg:col-span-2">
          <FleetManager robots={['pirc-01', 'pirc-02']} />
          <ARView />
        </div>
      </div>
    </div>
  );
}

export default App;
