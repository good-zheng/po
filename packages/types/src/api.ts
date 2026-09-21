export type Result<T> = {
  code: number;
  success: boolean;
  data: T;
  message: string;
};

export type PageResponse<T> = {
  content: T[];
  totalElements: number;
  totalPages: number;
  number: number;
  size: number;
};
