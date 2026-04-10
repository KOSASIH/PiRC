import React, { useState } from 'react';

function MissionPlanner({ ros }) {
  const [waypoints, setWaypoints] = useState([]);
  const [dragging, setDragging] = useState(false);

  const addWaypoint = (e) => {
    if (dragging) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width - 0.5) * 10;
    const y = (0.5 - (e.clientY - rect.top) / rect.height) * 10;
    
    const newWaypoint = { id: Date.now(), x, y };
    setWaypoints([...waypoints, newWaypoint]);
    
    // Send to Nav2
    if (ros) {
      const goal = new ROSLIB.Message({
        header: { frame_id: 'map' },
        pose: { position: { x, y, z: 0 }, orientation: { w: 1 } }
      });
      const goalTopic = new ROSLIB.Topic({
        ros: ros,
        name: '/goal_pose',
        messageType: 'geometry_msgs/PoseStamped'
      });
      goalTopic.publish(goal);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between">
        <h3>Drag to add waypoints</h3>
        <button 
          className="bg-green-500 px-4 py-2 rounded"
          onClick={() => setWaypoints([])}
        >
          Clear Mission
        </button>
      </div>
      
      <div 
        className="w-full h-96 bg-gradient-to-br from-gray-700 to-gray-900 rounded-lg relative cursor-crosshair"
        onMouseDown={() => setDragging(true)}
        onMouseUp={() => setDragging(false)}
        onClick={addWaypoint}
      >
        {/* Waypoints */}
        {waypoints.map(wp => (
          <div
            key={wp.id}
            className="absolute w-4 h-4 bg-blue-500 rounded-full transform -translate-x-2 -translate-y-2 shadow-lg"
            style={{ 
              left: `calc(50% + ${wp.x * 2}%)`, 
              top: `calc(50% + ${wp.y * 2}%)` 
            }}
          />
        ))}
        
        {/* Path preview */}
        {waypoints.length > 1 && (
          <svg className="absolute inset-0 w-full h-full">
            {waypoints.map((wp, i) => 
              i < waypoints.length - 1 && (
                <line
                  key={i}
                  x1={`calc(50% + ${wp.x * 2}%)`}
                  y1={`calc(50% + ${wp.y * 2}%)`}
                  x2={`calc(50% + ${waypoints[i+1].x * 2}%)`}
                  y2={`calc(50% + ${waypoints[i+1].y * 2}%)`}
                  stroke="rgba(59, 130, 246, 0.5)"
                  strokeWidth="3"
                />
              )
            )}
          </svg>
        )}
      </div>
      
      <div className="text-sm text-gray-400">
        {waypoints.length} waypoints • Click to add • Drag to map
      </div>
    </div>
  );
}

export default MissionPlanner;
