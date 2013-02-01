function tokenize(text, word) {
				var tokenized = {};
				tokenized['left'] = [];
				tokenized['right'] = [];
					
				var sentences = text.split("\n");
				for(var i = 0;i < sentences.length;i++){
					if (sentences[i].indexOf(word) > 0) {
						//Inventar jeito para lidar com mais de uma ocorrencia na frase
						var left = sentences[i].split(word)[0];
						var right = sentences[i].split(word)[1];
						var trimmed_right = right.replace(/^\s+|\s+$/g, '').split(" ");
						var trimmed_left = left.replace(/^\s+|\s+$/g, '').split(" ");
						tokenized['left'].push(trimmed_left);
						tokenized['right'].push(trimmed_right);
					}
				}
				return tokenized;
			}

function createTree(data, context, container) {
    var myTree = null;
    var lefts = data['left'];
    for(var i = 0; i < lefts.length; i++){
        lefts[i] = lefts[i].reverse();
    }
    var rights = data['right'];
    var w = 1000,
    h = 150,
    detail = 100 /* % */;
    var paper = Raphael(container, w, h);
    makeWordTree(rights, context, detail, container, w, h, WordTree.RO_LEFT, paper);	
    makeWordTree(lefts, context, detail, container, w, h, WordTree.RO_RIGHT, paper);				
}
