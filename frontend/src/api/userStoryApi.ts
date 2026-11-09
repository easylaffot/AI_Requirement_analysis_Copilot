import { apiClient } from "./apiClient";

import type {
  UserStoryGenerationRequest,
  UserStoryGenerationResponse,
} from "../types/userStory";

export async function generateUserStories(
  request: UserStoryGenerationRequest
): Promise<UserStoryGenerationResponse> {
  const response = await apiClient.post<UserStoryGenerationResponse>(
    "/api/user-stories/generate",
    request
  );

  return response.data;
}
