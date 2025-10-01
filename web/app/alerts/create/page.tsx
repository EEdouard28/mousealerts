/**
 * Alert Creation Page
 * 
 * This page allows users to create new Disney dining alerts.
 * Features:
 * - Restaurant search and selection
 * - Date and time pickers
 * - Party size selection
 * - Notification preferences
 * - Form validation and submission
 * - Real-time feedback and error handling
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import ProtectedRoute from '@/components/ProtectedRoute';
import { 
  ArrowLeftIcon,
  MagnifyingGlassIcon,
  CalendarIcon,
  ClockIcon,
  UserGroupIcon,
  BellIcon,
  CheckCircleIcon,
  XMarkIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

// Complete Disney World restaurants database
const DISNEY_RESTAURANTS = [
  // Magic Kingdom
  { id: 1, name: 'Be Our Guest Restaurant', park: 'Magic Kingdom', type: 'Table Service' },
  { id: 2, name: 'Cinderella\'s Royal Table', park: 'Magic Kingdom', type: 'Character Dining' },
  { id: 3, name: 'Jungle Navigation Co. Ltd. Skipper Canteen', park: 'Magic Kingdom', type: 'Table Service' },
  { id: 4, name: 'The Plaza Restaurant', park: 'Magic Kingdom', type: 'Table Service' },
  { id: 5, name: 'Tony\'s Town Square Restaurant', park: 'Magic Kingdom', type: 'Table Service' },
  { id: 6, name: 'Crystal Palace', park: 'Magic Kingdom', type: 'Character Dining' },
  { id: 7, name: 'Liberty Tree Tavern', park: 'Magic Kingdom', type: 'Table Service' },
  { id: 8, name: 'The Diamond Horseshoe', park: 'Magic Kingdom', type: 'Table Service' },
  { id: 9, name: 'Casey\'s Corner', park: 'Magic Kingdom', type: 'Quick Service' },
  { id: 10, name: 'Columbia Harbour House', park: 'Magic Kingdom', type: 'Quick Service' },
  { id: 11, name: 'Cosmic Ray\'s Starlight Café', park: 'Magic Kingdom', type: 'Quick Service' },
  { id: 12, name: 'Pecos Bill Tall Tale Inn and Café', park: 'Magic Kingdom', type: 'Quick Service' },
  { id: 13, name: 'Pinocchio Village Haus', park: 'Magic Kingdom', type: 'Quick Service' },
  { id: 14, name: 'Sleepy Hollow', park: 'Magic Kingdom', type: 'Quick Service' },
  { id: 15, name: 'The Friar\'s Nook', park: 'Magic Kingdom', type: 'Quick Service' },

  // EPCOT
  { id: 16, name: 'Akershus Royal Banquet Hall', park: 'EPCOT', type: 'Character Dining' },
  { id: 17, name: 'Le Cellier Steakhouse', park: 'EPCOT', type: 'Table Service' },
  { id: 18, name: 'Rose & Crown Dining Room', park: 'EPCOT', type: 'Table Service' },
  { id: 19, name: 'San Angel Inn Restaurante', park: 'EPCOT', type: 'Table Service' },
  { id: 20, name: 'Teppan Edo', park: 'EPCOT', type: 'Table Service' },
  { id: 21, name: 'Biergarten Restaurant', park: 'EPCOT', type: 'Table Service' },
  { id: 22, name: 'Chefs de France', park: 'EPCOT', type: 'Table Service' },
  { id: 23, name: 'Coral Reef Restaurant', park: 'EPCOT', type: 'Table Service' },
  { id: 24, name: 'Garden Grill Restaurant', park: 'EPCOT', type: 'Character Dining' },
  { id: 25, name: 'La Hacienda de San Angel', park: 'EPCOT', type: 'Table Service' },
  { id: 26, name: 'La Cantina de San Angel', park: 'EPCOT', type: 'Quick Service' },
  { id: 27, name: 'Les Halles Boulangerie-Patisserie', park: 'EPCOT', type: 'Quick Service' },
  { id: 28, name: 'Lotus Blossom Café', park: 'EPCOT', type: 'Quick Service' },
  { id: 29, name: 'Nine Dragons Restaurant', park: 'EPCOT', type: 'Table Service' },
  { id: 30, name: 'Regal Eagle Smokehouse', park: 'EPCOT', type: 'Quick Service' },
  { id: 31, name: 'Restaurant Marrakesh', park: 'EPCOT', type: 'Table Service' },
  { id: 32, name: 'Spice Road Table', park: 'EPCOT', type: 'Table Service' },
  { id: 33, name: 'Sunshine Seasons', park: 'EPCOT', type: 'Quick Service' },
  { id: 34, name: 'Tangierine Café', park: 'EPCOT', type: 'Quick Service' },
  { id: 35, name: 'The Garden Grill', park: 'EPCOT', type: 'Character Dining' },
  { id: 36, name: 'Via Napoli Ristorante e Pizzeria', park: 'EPCOT', type: 'Table Service' },
  { id: 37, name: 'Yorkshire County Fish Shop', park: 'EPCOT', type: 'Quick Service' },

  // Animal Kingdom
  { id: 38, name: 'Tusker House Restaurant', park: 'Animal Kingdom', type: 'Character Dining' },
  { id: 39, name: 'Yak & Yeti Restaurant', park: 'Animal Kingdom', type: 'Table Service' },
  { id: 40, name: 'Rainforest Café', park: 'Animal Kingdom', type: 'Table Service' },
  { id: 41, name: 'Tiffins', park: 'Animal Kingdom', type: 'Table Service' },
  { id: 42, name: 'Yak & Yeti Local Food Cafes', park: 'Animal Kingdom', type: 'Quick Service' },
  { id: 43, name: 'Flame Tree Barbecue', park: 'Animal Kingdom', type: 'Quick Service' },
  { id: 44, name: 'Harambe Market', park: 'Animal Kingdom', type: 'Quick Service' },
  { id: 45, name: 'Pizzafari', park: 'Animal Kingdom', type: 'Quick Service' },
  { id: 46, name: 'Restaurantosaurus', park: 'Animal Kingdom', type: 'Quick Service' },
  { id: 47, name: 'Satu\'li Canteen', park: 'Animal Kingdom', type: 'Quick Service' },
  { id: 48, name: 'The Smiling Crocodile', park: 'Animal Kingdom', type: 'Quick Service' },
  { id: 49, name: 'Trilo-Bites', park: 'Animal Kingdom', type: 'Quick Service' },

  // Hollywood Studios
  { id: 50, name: '50\'s Prime Time Café', park: 'Hollywood Studios', type: 'Table Service' },
  { id: 51, name: 'Hollywood & Vine', park: 'Hollywood Studios', type: 'Character Dining' },
  { id: 52, name: 'Mama Melrose\'s Ristorante Italiano', park: 'Hollywood Studios', type: 'Table Service' },
  { id: 53, name: 'Sci-Fi Dine-In Theater Restaurant', park: 'Hollywood Studios', type: 'Table Service' },
  { id: 54, name: 'The Hollywood Brown Derby', park: 'Hollywood Studios', type: 'Table Service' },
  { id: 55, name: 'BaseLine Tap House', park: 'Hollywood Studios', type: 'Quick Service' },
  { id: 56, name: 'Docking Bay 7 Food and Cargo', park: 'Hollywood Studios', type: 'Quick Service' },
  { id: 57, name: 'Fairfax Fare', park: 'Hollywood Studios', type: 'Quick Service' },
  { id: 58, name: 'Hollywood Scoops', park: 'Hollywood Studios', type: 'Quick Service' },
  { id: 59, name: 'Kat Saka\'s Kettle', park: 'Hollywood Studios', type: 'Quick Service' },
  { id: 60, name: 'Market', park: 'Hollywood Studios', type: 'Quick Service' },
  { id: 61, name: 'Oga\'s Cantina', park: 'Hollywood Studios', type: 'Lounge' },
  { id: 62, name: 'PizzeRizzo', park: 'Hollywood Studios', type: 'Quick Service' },
  { id: 63, name: 'Ronto Roasters', park: 'Hollywood Studios', type: 'Quick Service' },
  { id: 64, name: 'The Trolley Car Café', park: 'Hollywood Studios', type: 'Quick Service' },
  { id: 65, name: 'Woody\'s Lunch Box', park: 'Hollywood Studios', type: 'Quick Service' },

  // Disney Springs
  { id: 66, name: 'The Boathouse', park: 'Disney Springs', type: 'Table Service' },
  { id: 67, name: 'Chef Art Smith\'s Homecomin\'', park: 'Disney Springs', type: 'Table Service' },
  { id: 68, name: 'D-Luxe Burger', park: 'Disney Springs', type: 'Quick Service' },
  { id: 69, name: 'Frontera Cocina', park: 'Disney Springs', type: 'Table Service' },
  { id: 70, name: 'Jaleo', park: 'Disney Springs', type: 'Table Service' },
  { id: 71, name: 'Jock Lindsey\'s Hangar Bar', park: 'Disney Springs', type: 'Lounge' },
  { id: 72, name: 'Morimoto Asia', park: 'Disney Springs', type: 'Table Service' },
  { id: 73, name: 'Paddlefish', park: 'Disney Springs', type: 'Table Service' },
  { id: 74, name: 'Raglan Road Irish Pub and Restaurant', park: 'Disney Springs', type: 'Table Service' },
  { id: 75, name: 'The Edison', park: 'Disney Springs', type: 'Table Service' },
  { id: 76, name: 'Wine Bar George', park: 'Disney Springs', type: 'Table Service' },
  { id: 77, name: 'Wolfgang Puck Bar & Grill', park: 'Disney Springs', type: 'Table Service' },

  // Disney Resorts
  { id: 78, name: 'California Grill', park: 'Contemporary Resort', type: 'Table Service' },
  { id: 79, name: 'Chef Mickey\'s', park: 'Contemporary Resort', type: 'Character Dining' },
  { id: 80, name: 'The Wave... of American Flavors', park: 'Contemporary Resort', type: 'Table Service' },
  { id: 81, name: 'Beaches & Cream Soda Shop', park: 'Beach Club Resort', type: 'Table Service' },
  { id: 82, name: 'Cape May Café', park: 'Beach Club Resort', type: 'Character Dining' },
  { id: 83, name: 'Martha\'s Vineyard', park: 'Beach Club Resort', type: 'Lounge' },
  { id: 84, name: 'Yachtsman Steakhouse', park: 'Yacht Club Resort', type: 'Table Service' },
  { id: 85, name: 'Ale & Compass Restaurant', park: 'Yacht Club Resort', type: 'Table Service' },
  { id: 86, name: 'Boma - Flavors of Africa', park: 'Animal Kingdom Lodge', type: 'Table Service' },
  { id: 87, name: 'Jiko - The Cooking Place', park: 'Animal Kingdom Lodge', type: 'Table Service' },
  { id: 88, name: 'Sanaa', park: 'Animal Kingdom Lodge', type: 'Table Service' },
  { id: 89, name: 'The Mara', park: 'Animal Kingdom Lodge', type: 'Quick Service' },
  { id: 90, name: 'Victoria Falls Lounge', park: 'Animal Kingdom Lodge', type: 'Lounge' },
  { id: 91, name: 'Kona Café', park: 'Polynesian Resort', type: 'Table Service' },
  { id: 92, name: 'Ohana', park: 'Polynesian Resort', type: 'Character Dining' },
  { id: 93, name: 'Trader Sam\'s Grog Grotto', park: 'Polynesian Resort', type: 'Lounge' },
  { id: 94, name: 'Kona Island', park: 'Polynesian Resort', type: 'Quick Service' },
  { id: 95, name: 'Pineapple Lanai', park: 'Polynesian Resort', type: 'Quick Service' },
  { id: 96, name: 'Spirit of Aloha Dinner Show', park: 'Polynesian Resort', type: 'Dinner Show' },
  { id: 97, name: 'Tonga Toast', park: 'Polynesian Resort', type: 'Quick Service' },
  { id: 98, name: '1900 Park Fare', park: 'Grand Floridian Resort', type: 'Character Dining' },
  { id: 99, name: 'Cítricos', park: 'Grand Floridian Resort', type: 'Table Service' },
  { id: 100, name: 'Grand Floridian Café', park: 'Grand Floridian Resort', type: 'Table Service' },
  { id: 101, name: 'Narcoossee\'s', park: 'Grand Floridian Resort', type: 'Table Service' },
  { id: 102, name: 'Victoria & Albert\'s', park: 'Grand Floridian Resort', type: 'Fine Dining' },
  { id: 103, name: 'Gasparilla Island Grill', park: 'Grand Floridian Resort', type: 'Quick Service' },
  { id: 104, name: 'Mizner\'s Lounge', park: 'Grand Floridian Resort', type: 'Lounge' },
  { id: 105, name: 'Enchanted Rose', park: 'Grand Floridian Resort', type: 'Lounge' }
];

const TIME_SLOTS = [
  '7:00 AM', '7:30 AM', '8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM',
  '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM',
  '1:00 PM', '1:30 PM', '2:00 PM', '2:30 PM', '3:00 PM', '3:30 PM',
  '4:00 PM', '4:30 PM', '5:00 PM', '5:30 PM', '6:00 PM', '6:30 PM',
  '7:00 PM', '7:30 PM', '8:00 PM', '8:30 PM', '9:00 PM', '9:30 PM',
  '10:00 PM', '10:30 PM'
];

export default function CreateAlertPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRestaurant, setSelectedRestaurant] = useState<any>(null);
  const [showRestaurantList, setShowRestaurantList] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    restaurant: '',
    park: '',
    date: '',
    time: '',
    partySize: 2,
    notifications: {
      sms: true,
      email: false,
      push: true
    },
    notes: ''
  });

  const [errors, setErrors] = useState<Record<string, string | null>>({});

  // Filter restaurants based on search
  const filteredRestaurants = DISNEY_RESTAURANTS.filter(restaurant =>
    restaurant.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    restaurant.park.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleRestaurantSelect = (restaurant: any) => {
    setSelectedRestaurant(restaurant);
    setFormData(prev => ({
      ...prev,
      restaurant: restaurant.name,
      park: restaurant.park
    }));
    setSearchQuery(restaurant.name);
    setShowRestaurantList(false);
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field as keyof typeof errors]) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  const handleNotificationChange = (type: string, checked: boolean) => {
    setFormData(prev => ({
      ...prev,
      notifications: {
        ...prev.notifications,
        [type]: checked
      }
    }));
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.restaurant) {
      newErrors.restaurant = 'Please select a restaurant';
    }
    if (!formData.date) {
      newErrors.date = 'Please select a date';
    }
    if (!formData.time) {
      newErrors.time = 'Please select a time';
    }
    if (formData.partySize < 1 || formData.partySize > 20) {
      newErrors.partySize = 'Party size must be between 1 and 20';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast.error('Please fix the errors below');
      return;
    }

    setIsSubmitting(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast.success('Alert created successfully! 🎉');
      router.push('/dashboard');
    } catch (error) {
      toast.error('Failed to create alert. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getMinDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  const getMaxDate = () => {
    const maxDate = new Date();
    maxDate.setDate(maxDate.getDate() + 60); // 60 days in advance
    return maxDate.toISOString().split('T')[0];
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
        {/* Header */}
        <div className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center py-4">
              <button
                onClick={() => router.back()}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors mr-4"
              >
                <ArrowLeftIcon className="w-5 h-5" />
                <span>Back</span>
              </button>
              
              <div className="flex items-center space-x-3">
                <div className="magic-glow">
                  <SparklesIcon className="w-8 h-8 text-primary-500" />
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Create Alert</h1>
                  <p className="text-sm text-gray-500">Set up your Disney dining alert</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Form */}
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Restaurant Selection */}
            <div className="card p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Restaurant Selection</h2>
              
              <div className="relative">
                <div className="relative">
                  <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search for a restaurant..."
                    value={searchQuery}
                    onChange={(e) => {
                      setSearchQuery(e.target.value);
                      setShowRestaurantList(true);
                    }}
                    onFocus={() => setShowRestaurantList(true)}
                    className={`w-full pl-10 pr-4 py-3 border-2 rounded-xl focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all duration-200 bg-white ${
                      errors.restaurant ? 'border-red-300' : 'border-gray-300'
                    }`}
                    style={{
                      WebkitAppearance: 'none',
                      MozAppearance: 'none',
                      appearance: 'none',
                      borderRadius: '12px'
                    }}
                  />
                </div>
                
                {showRestaurantList && (
                  <div className="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-xl shadow-lg max-h-60 overflow-y-auto">
                    {filteredRestaurants.length > 0 ? (
                      filteredRestaurants.map((restaurant) => (
                        <button
                          key={restaurant.id}
                          type="button"
                          onClick={() => handleRestaurantSelect(restaurant)}
                          className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0"
                        >
                          <div className="font-medium text-gray-900">{restaurant.name}</div>
                          <div className="text-sm text-gray-500">{restaurant.park} • {restaurant.type}</div>
                        </button>
                      ))
                    ) : (
                      <div className="px-4 py-3 text-gray-500">No restaurants found</div>
                    )}
                  </div>
                )}
              </div>
              
              {errors.restaurant && (
                <p className="mt-2 text-sm text-red-600">{errors.restaurant}</p>
              )}
              
              {selectedRestaurant && (
                <div className="mt-4 p-4 bg-primary-50 rounded-xl">
                  <div className="flex items-center space-x-2">
                    <CheckCircleIcon className="w-5 h-5 text-primary-600" />
                    <span className="font-medium text-primary-900">Selected: {selectedRestaurant.name}</span>
                  </div>
                  <p className="text-sm text-primary-700 mt-1">{selectedRestaurant.park} • {selectedRestaurant.type}</p>
                </div>
              )}
            </div>

            {/* Date and Time */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Date</h3>
                <div className="relative">
                  <CalendarIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="date"
                    value={formData.date}
                    onChange={(e) => handleInputChange('date', e.target.value)}
                    min={getMinDate()}
                    max={getMaxDate()}
                    className={`w-full pl-10 pr-4 py-3 border-2 rounded-xl focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all duration-200 bg-white ${
                      errors.date ? 'border-red-300' : 'border-gray-300'
                    }`}
                    style={{
                      WebkitAppearance: 'none',
                      MozAppearance: 'none',
                      appearance: 'none',
                      borderRadius: '12px'
                    }}
                  />
                </div>
                {errors.date && (
                  <p className="mt-2 text-sm text-red-600">{errors.date}</p>
                )}
              </div>

              <div className="card p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Time</h3>
                <div className="relative">
                  <ClockIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <select
                    value={formData.time}
                    onChange={(e) => handleInputChange('time', e.target.value)}
                    className={`w-full pl-10 pr-4 py-3 border-2 rounded-xl focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all duration-200 bg-white ${
                      errors.time ? 'border-red-300' : 'border-gray-300'
                    }`}
                    style={{
                      WebkitAppearance: 'none',
                      MozAppearance: 'none',
                      appearance: 'none',
                      borderRadius: '12px'
                    }}
                  >
                    <option value="">Select a time</option>
                    {TIME_SLOTS.map((time) => (
                      <option key={time} value={time}>{time}</option>
                    ))}
                  </select>
                </div>
                {errors.time && (
                  <p className="mt-2 text-sm text-red-600">{errors.time}</p>
                )}
              </div>
            </div>

            {/* Party Size */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Party Size</h3>
              <div className="flex items-center space-x-4">
                <UserGroupIcon className="w-6 h-6 text-gray-400" />
                <div className="flex items-center space-x-2">
                  <button
                    type="button"
                    onClick={() => handleInputChange('partySize', Math.max(1, formData.partySize - 1))}
                    className="w-10 h-10 rounded-full border-2 border-gray-300 flex items-center justify-center hover:border-primary-500 transition-colors"
                  >
                    <span className="text-gray-600">-</span>
                  </button>
                  <span className="w-16 text-center text-lg font-semibold">{formData.partySize}</span>
                  <button
                    type="button"
                    onClick={() => handleInputChange('partySize', Math.min(20, formData.partySize + 1))}
                    className="w-10 h-10 rounded-full border-2 border-gray-300 flex items-center justify-center hover:border-primary-500 transition-colors"
                  >
                    <span className="text-gray-600">+</span>
                  </button>
                </div>
                <span className="text-sm text-gray-500">people</span>
              </div>
              {errors.partySize && (
                <p className="mt-2 text-sm text-red-600">{errors.partySize}</p>
              )}
            </div>

            {/* Notification Preferences */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Notification Preferences</h3>
              <div className="space-y-4">
                <label className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    checked={formData.notifications.sms}
                    onChange={(e) => handleNotificationChange('sms', e.target.checked)}
                    className="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <div className="flex items-center space-x-2">
                    <BellIcon className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-700">SMS notifications</span>
                  </div>
                </label>
                
                <label className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    checked={formData.notifications.push}
                    onChange={(e) => handleNotificationChange('push', e.target.checked)}
                    className="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <div className="flex items-center space-x-2">
                    <BellIcon className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-700">Push notifications</span>
                  </div>
                </label>
              </div>
            </div>

            {/* Additional Notes */}
            <div className="card p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Additional Notes (Optional)</h3>
              <textarea
                value={formData.notes}
                onChange={(e) => handleInputChange('notes', e.target.value)}
                placeholder="Any special requests or notes for this alert..."
                rows={3}
                className="w-full px-4 py-3 border-2 border-gray-300 rounded-xl focus:border-primary-500 focus:ring-2 focus:ring-primary-200 outline-none transition-all duration-200 bg-white resize-none"
                style={{
                  WebkitAppearance: 'none',
                  MozAppearance: 'none',
                  appearance: 'none',
                  borderRadius: '12px'
                }}
              />
            </div>

            {/* Submit Button */}
            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={() => router.back()}
                className="btn btn-outline"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="btn btn-primary flex items-center space-x-2"
              >
                {isSubmitting ? (
                  <>
                    <div className="loading-spinner w-4 h-4" />
                    <span>Creating Alert...</span>
                  </>
                ) : (
                  <>
                    <SparklesIcon className="w-5 h-5" />
                    <span>Create Alert</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </ProtectedRoute>
  );
}
