import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { PaperProvider } from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import { View, Text, ActivityIndicator } from 'react-native';
import { LineChart } from 'react-native-chart-kit';

const Tab = createBottomTabNavigator();

interface Wallet {
  address: string;
  balance_pi: number;
  balance_usd: number;
  pending_rewards: number;
}

const API_BASE = 'http://YOUR_IP:3000'; // Replace with your PiRC IP

const WalletScreen = () => {
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchWallet();
    const interval = setInterval(fetchWallet, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchWallet = async () => {
    try {
      const response = await axios.get(`${API_BASE}/wallet`);
      setWallet(response.data);
    } catch (error) {
      console.error('Wallet fetch failed:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#8B5CF6" />
      </View>
    );
  }

  return (
    <View style={{ flex: 1, padding: 20, backgroundColor: '#0F0F23' }}>
      <Text style={{ fontSize: 32, fontWeight: 'bold', color: 'white', marginBottom: 20 }}>
        💰 PiRC Wallet
      </Text>
      
      <View style={{ backgroundColor: '#1E1E3F', padding: 20, borderRadius: 20, marginBottom: 20 }}>
        <Text style={{ color: '#8B5CF6', fontSize: 24, fontWeight: 'bold' }}>
          {wallet?.balance_pi?.toFixed(2)} π
        </Text>
        <Text style={{ color: 'white', fontSize: 18 }}>
          ≈ ${(wallet?.balance_usd || 0).toFixed(2)} USD
        </Text>
      </View>

      <View style={{ flexDirection: 'row', justifyContent: 'space-around', marginBottom: 20 }}>
        <View style={{ alignItems: 'center' }}>
          <Text style={{ color: '#10B981', fontSize: 24, fontWeight: 'bold' }}>
            +{wallet?.pending_rewards?.toFixed(2)} π
          </Text>
          <Text style={{ color: 'white' }}>Pending</Text>
        </View>
        <View style={{ alignItems: 'center' }}>
          <Text style={{ color: '#F59E0B', fontSize: 24, fontWeight: 'bold' }}>
            {wallet?.address.slice(0, 8)}...
          </Text>
          <Text style={{ color: 'white' }}>Address</Text>
        </View>
      </View>

      <LineChart
        data={{
          labels: ['1h', '6h', '12h', '24h'],
          datasets: [{ data: [0.15, 0.152, 0.149, 0.155] }]
        }}
        width={350}
        height={220}
        chartConfig={{
          backgroundColor: '#0F0F23',
          backgroundGradientFrom: '#0F0F23',
          backgroundGradientTo: '#1E1E3F',
          decimalPlaces: 4,
          color: (opacity = 1) => `rgba(139, 92, 246, ${opacity})`,
          labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
        }}
        style={{ borderRadius: 16, marginBottom: 20 }}
      />
    </View>
  );
};

const TradingScreen = () => {
  const [status, setStatus] = useState({ pnl: 0, position: 0 });

  const startTrading = async () => {
    try {
      await axios.post(`${API_BASE}/trading/start`);
      alert('🤖 Auto-trading started!');
    } catch (error) {
      alert('Trading start failed');
    }
  };

  return (
    <View style={{ flex: 1, padding: 20, backgroundColor: '#0F0F23' }}>
      <Text style={{ fontSize: 28, fontWeight: 'bold', color: 'white', marginBottom: 30 }}>
        🤖 AI Trading
      </Text>
      
      <View style={{ backgroundColor: '#1E1E3F', padding: 25, borderRadius: 20, marginBottom: 20 }}>
        <Text style={{ color: '#10B981', fontSize: 36, fontWeight: 'bold' }}>
          +${status.pnl?.toFixed(2)}
        </Text>
        <Text style={{ color: 'white', fontSize: 16 }}>Total PnL</Text>
      </View>

      <Text style={{ color: 'white', fontSize: 20, marginBottom: 20 }}>
        Position: {status.position?.toFixed(1)} π
      </Text>

      <TouchableOpacity
        style={{
          backgroundColor: '#8B5CF6',
          padding: 20,
          borderRadius: 20,
          alignItems: 'center'
        }}
        onPress={startTrading}
      >
        <Text style={{ color: 'white', fontSize: 18, fontWeight: 'bold' }}>
          🚀 Start AI Trading
        </Text>
      </TouchableOpacity>
    </View>
  );
};

const App = () => {
  return (
    <PaperProvider>
      <NavigationContainer>
        <Tab.Navigator
          screenOptions={{
            tabBarActiveTintColor: '#8B5CF6',
            tabBarStyle: { backgroundColor: '#1E1E3F' },
            headerStyle: { backgroundColor: '#0F0F23' },
            headerTintColor: 'white',
          }}
        >
          <Tab.Screen
            name="Wallet"
            component={WalletScreen}
            options={{
              tabBarLabel: 'Wallet',
              tabBarIcon: ({ color }) => <Icon name="wallet" color={color} size={24} />,
            }}
          />
          <Tab.Screen
            name="Trading"
            component={TradingScreen}
            options={{
              tabBarLabel: 'Trading',
              tabBarIcon: ({ color }) => <Icon name="robot" color={color} size={24} />,
            }}
          />
        </Tab.Navigator>
      </NavigationContainer>
    </PaperProvider>
  );
};

export default App;
