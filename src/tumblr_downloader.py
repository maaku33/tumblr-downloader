
import argparse
import urllib.request
import shutil
import os
import errno
import pytumblr


_USAGE_DESCRIPTION = "Download liked posts of Tumblr profile."

_DEFAULT_POST_LIMIT = 20

_DEFAULT_POST_NUMBER = 10
_DEFAULT_DIRECTORY = "."


def parse_arguments():
    parser = argparse.ArgumentParser(description=_USAGE_DESCRIPTION)
    parser.add_argument("-d", "--directory",
                        metavar="DIR",
                        default=_DEFAULT_DIRECTORY,
                        help="directory where downloaded files will be stored")
    parser.add_argument("-n",
                        metavar="NUM",
                        type=int,
                        default=_DEFAULT_POST_NUMBER,
                        help="how many posts to download")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="explain what is being done")
    parser.add_argument("consumer_key",
                        help="Tumblr app consumer key")
    parser.add_argument("consumer_secret",
                        help="Tumblr app consumer secret")
    parser.add_argument("oauth_token",
                        help="Tumblr app oauth token")
    parser.add_argument("oauth_secret",
                        help="Tumblr app oauth secret")
    return parser.parse_args()


def create_directory(path):
    try:
        os.makedirs(path)
    except OSError as error:
        if error.errno != errno.EEXIST:
            raise


def save_file(url, filename):
    with urllib.request.urlopen(url) as response, open(filename, 'wb') as out_file:
        shutil.copyfileobj(response, out_file)


def download_likes(client, path, num, verbose):
    likes_count = 0
    before = None

    while likes_count < num:
        kwargs = {"limit": _DEFAULT_POST_LIMIT}
        if before is not None:
            kwargs["before"] = before

        response = client.likes(**kwargs)

        before = response["_links"]["next"]["query_params"]["before"]

        for like in response["liked_posts"]:
            if "photos" in like:
                for photo in like["photos"]:
                    url = photo["original_size"]["url"]

                    filename = url.split("/")[-1]
                    pathname = path + "/" + filename

                    if not os.path.isfile(pathname):
                        if verbose:
                            print("Downloading file {}".format(url))
                        save_file(url, pathname)
                    elif verbose:
                        print("Photo {} already exists".format(filename))

            likes_count += 1
            if likes_count >= num:
                break

    client.likes()


def main():
    args = parse_arguments()

    path = args.directory
    create_directory(path)

    client = pytumblr.TumblrRestClient(
        args.consumer_key,
        args.consumer_secret,
        args.oauth_token,
        args.oauth_secret
    )

    download_likes(client, path, args.n, args.verbose)


if __name__ == "__main__":
    main()
