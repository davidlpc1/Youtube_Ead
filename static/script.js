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

const like_button = document.querySelector('.youtube-like-button')
const dislike_button = document.querySelector('.youtube-dislike-button')
const dislike_span = document.querySelector('.youtube-dislikes')
const like_span = document.querySelector('.youtube-likes')
const disableColor = 'rgb(144, 144, 144)'
const activeColor = 'rgb(6, 95, 212)'
if(like_button !== null){
    const linkToLike = `${location.pathname}/like`
    const linkToDislike = `${location.pathname}/dislike`
    const like_button_svg = like_button.firstElementChild
    const dislike_button_svg = dislike_button.firstElementChild

    like_button.addEventListener('click', async () => {
        if(like_button_svg.style.fill == disableColor) {
            like_button_svg.style.fill = activeColor
            dislike_button_svg.style.fill = disableColor

            like_span.innerHTML = `${Number(like_span.innerHTML) + 1 < 0 ? 0 : Number(like_span.innerHTML) + 1 }`
            dislike_span.innerHTML =  `${Number(dislike_span.innerHTML) - 1 < 0 ? 0 : Number(dislike_span.innerHTML) - 1 }`

            await fetch(linkToLike, {
                method: "POST"
            })
        }
        else{
            like_button_svg.style.fill = disableColor
            like_span.innerHTML = `${Number(like_span.innerHTML) - 1 < 0 ? 0 : Number(like_span.innerHTML) - 1 }`
        }
    })

    dislike_button.addEventListener('click', async () => {
        if( dislike_button_svg.style.fill == disableColor)   {
            dislike_button_svg.style.fill = activeColor
            like_button_svg.style.fill = disableColor

            like_span.innerHTML =  `${Number(like_span.innerHTML) - 1 < 0 ? 0 : Number(like_span.innerHTML) - 1 }`
            dislike_span.innerHTML =  `${Number(dislike_span.innerHTML) + 1 < 0 ? 0 : Number(dislike_span.innerHTML) + 1 }`

            await fetch(linkToDislike, {
                method: "POST"
            })
        }
        else{
            dislike_button_svg.style.fill = disableColor
            dislike_span.innerHTML =  `${Number(dislike_span.innerHTML) - 1 < 0 ? 0 : Number(dislike_span.innerHTML) - 1 }`
        }
    })
}