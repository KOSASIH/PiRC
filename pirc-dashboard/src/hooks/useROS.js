import { useState, useEffect } from 'react';
import ROSLIB from 'roslib';

export function useROS(websocketUrl) {
  const [ros, setRos] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const rosInstance = new ROSLIB.Ros({
      url: websocketUrl
    });

    rosInstance.on('connection', () => {
      setConnected(true);
      setRos(rosInstance);
    });

    rosInstance.on('error', (error) => {
      console.error('ROS Error:', error);
      setConnected(false);
    });

    rosInstance.on('close', () => {
      setConnected(false);
      setRos(null);
    });

    return () => {
      rosInstance.close();
    };
  }, [websocketUrl]);

  return { ros, connected };
}
