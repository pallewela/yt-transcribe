import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
});

export async function submitVideos(urls) {
  const { data } = await api.post('/videos/batch', { urls });
  return data;
}

export async function getVideos(status = null) {
  const params = status ? { status } : {};
  const { data } = await api.get('/videos', { params });
  return data;
}

export async function getVideo(id) {
  const { data } = await api.get(`/videos/${id}`);
  return data;
}

export async function deleteVideo(id) {
  const { data } = await api.delete(`/videos/${id}`);
  return data;
}
