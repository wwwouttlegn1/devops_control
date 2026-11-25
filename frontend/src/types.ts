export interface Medicine {
  id: number;
  name: string;
  price: string | number;
  quantity: number;
  prescription: boolean;
}

export interface DeliveryEstimate {
  district: string;
  days: number;
}

