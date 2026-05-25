import request from '../utils/request';

export const aiService = {
  /**
   * 发送问题并获取 DeepSeek 回复
   * @param {string} question - 用户提出的问题
   * @param {Array} history - 对话历史，用于上下文关联
   */
  async askQuestion(question, history = []) {
    return request.post('/chat', {
      question: question,
      history: history
    });
  }
};