export type UserItem = {
  id: number;
  username: string;
  email?: string | null;
  nickname?: string | null;
  avatar?: string | null;
  firstName?: string | null;
  lastName?: string | null;
  phoneNumber?: string | null;
  role: string;
  status: string;
  createTime?: string;
  updateTime?: string;
};

export type UserRequest = {
  username: string;
  password?: string;
  email?: string;
  firstName?: string;
  lastName?: string;
  phoneNumber?: string;
  role?: string;
  status?: string;
  nickname?: string;
  avatar?: string;
};

export type ProfileRequest = {
  nickname?: string;
  email?: string;
  phoneNumber?: string;
  avatar?: string;
};

export type ChangePasswordRequest = {
  oldPassword: string;
  newPassword: string;
};
