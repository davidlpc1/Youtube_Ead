function getYouTubeThumbnail(youtubeURL) {
    const youtubeId = youtubeURL
        .replace(
            /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/,
            '$7',
        );
    return youtubeId
}

const thumbnails = document.querySelectorAll('img.youtube_thumbnail')
if (thumbnails.length > 0) {
    thumbnails.forEach(thumbnail => {
        thumbnail.src = `https://img.youtube.com/vi/${getYouTubeThumbnail(thumbnail.dataset.url)}/hqdefault.jpg`
    })
}

const video = document.querySelector('iframe.youtube-video')
if (video !== null) {
    video.src = `https://www.youtube.com/embed/${getYouTubeThumbnail(video.dataset.url)}`
}

