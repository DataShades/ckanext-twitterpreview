$( document ).ready(function() {
	// jQuery('.twitter-feed-text-post-link').on('click', function () {
	// 	 window.location=$(this).children(".twitter-feed-post-link").attr("href");
	// 	 $( this ).attr( 'target', '_blank' );
	// 	 return false;
	// });
	jQuery('.twitter-feed-content a').attr( 'target', '_blank' );
});