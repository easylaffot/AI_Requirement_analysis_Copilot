import axios from "axios";

import type {
  UserStoryGenerationRequest,
  UserStoryGenerationResponse,
} from "../types/userStory";

export async function generateUserStories(
  request: UserStoryGenerationRequest
): Promise<UserStoryGenerationResponse> {
  const response = await axios.post<UserStoryGenerationResponse>(
    "/api/user-stories/generate",
    request
  );

  return response.data;
}
