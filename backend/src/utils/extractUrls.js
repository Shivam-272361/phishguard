export const extractUrls = (text) => {

    return text.match(
        /https?:\/\/[^\s]+|www\.[^\s]+/gi
    ) || [];

};
